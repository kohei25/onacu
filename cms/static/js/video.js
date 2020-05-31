const Peer = window.Peer;
// jquery
(async function main() {
  // videochat
  const localVideo = $('#localVideo');
  const remoteVideo = $('#remoteVideo');
  const eventId =$('#js-event').attr('value');

  // TODO: audio false -> true
  const localStream = await navigator.mediaDevices
    .getUserMedia({
      audio: true,
      video: true,
    })
    .catch(console.error);
  
  // Render local stream
  localVideo.get(0).muted = true;
  localVideo.get(0).srcObject = localStream;
  localVideo.get(0).playsInline = true;
  await localVideo.get(0).play().catch(console.error);

  const peer = new Peer({
    key: '889cd639-6a9e-4947-b168-35ad15fb44cb',
    debug: 3,
  });

  function makeCalll(remotePeerId, ticketOrder, lastTicket, personalTime){
    if (!peer.open) {
      return;
    }

    const mediaConnection = peer.call(remotePeerId, localStream);

    mediaConnection.on('stream', async function(stream){
      remoteVideo.get(0).srcObject = stream;
      remoteVideo.get(0).playsInline = true;
      await remoteVideo.get(0).play().catch(console.error);
    });

    mediaConnection.once('close', function(){
      remoteVideo.get(0).srcObject.getTracks().forEach(function(track){track.stop()});
      remoteVideo.get(0).srcObject = null;
    });

    function closeFunc() {
      mediaConnection.close(true);
      console.log(personalTime)
      ticketOrder += 1
      getPeerId(ticketOrder, lastTicket, personalTime);
    }

    console.log(personalTime*1000)
    setTimeout(closeFunc, personalTime*1000);
  };

  function postPeerId(peerId) {
    let ticketId = $('#js-ticket').attr('value')
    $.ajax({
      url: '/ajax/ticket/post',
      data: {
        'userPeerId': peerId,
        'ticketId': ticketId,
      },
      dataType: 'json',
      success: function (data) {

      }
    })
  }

  // User側のaction
  peer.on('open', function () {
    if ($('#js-user').length) {
      postPeerId(peer.id);
    }
  });

  // host function!!
  // Host側のaction
  $('#js-start').click(function(){
    const lastTicket = $('#js-lastTicket').attr('value')
    const personalTime = $('#js-personalTime').attr('value')
    getPeerId(1, lastTicket, personalTime)
  })

  function getPeerId(ticketOrder, lastTicket, personalTime) {

    if(ticketOrder <= lastTicket){
      $.ajax({
        url: '/ajax/ticket/get',
        data: {
          'eventId': eventId,
          'ticketOrder': ticketOrder,
        },
        dataType: 'json',
      }).done(function (data) {
        if(data.userPeerId != 0){
          makeCalll(data.userPeerId, ticketOrder, lastTicket, personalTime)
        }else{
          console.log('skip')
          ticketOrder += 1
          getPeerId(ticketOrder, lastTicket)
        }
      })
    }else{
      let finUrl = '/event/' + eventId + '/finish'
      window.location.href = finUrl;
    }

  }

  // Register callee handler
  // call function
  peer.on('call', function(mediaConnection){
    mediaConnection.answer(localStream);

    mediaConnection.on('stream', async function(stream){
      // Render remote stream for callee
      remoteVideo.get(0).srcObject = stream;
      remoteVideo.get(0).playsInline = true;
      await remoteVideo.get(0).play().catch(console.error);
    });

    mediaConnection.once('close', function(){
      remoteVideo.get(0).srcObject.getTracks().forEach(function(track){track.stop()});
      remoteVideo.get(0).srcObject = null;
      let finUrl = '/event/' + eventId + '/finish'
      window.location.href = finUrl;
    });

  });

  peer.on('error', console.error);
})();