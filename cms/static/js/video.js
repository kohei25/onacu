var videoChat = async () => {
  $('#note').modal('show'); // 注意事項を表示
  // videochat
  const localVideo = $('#localVideo');
  const remoteVideo = $('#remoteVideo');
  const eventId = $('#js-event').attr('value');
  const pleaseWait = $('#pleaseWait');

  const localStream = await navigator.mediaDevices
    .getUserMedia({
      video: {
        aspectRatio: 1,
        facingMode: 'user',
        resizeMode: 'none'
      },
      audio: {
        autoGainControl: true,
        echoCancellation: true,
        noiseSuppression: true
      }
    })
    .catch(console.error);

  // Render local stream
  localVideo.get(0).muted = true;
  localVideo.get(0).srcObject = localStream;
  localVideo.get(0).playsInline = true;
  await localVideo.get(0).play().catch(console.error);

  const peer = new Peer({
    key: '889cd639-6a9e-4947-b168-35ad15fb44cb',
  });

  function makeCalll(remotePeerId, ticketOrder, lastTicket, personalTime) {
    if (!peer.open) {
      return;
    }

    const mediaConnection = peer.call(remotePeerId, localStream);

    mediaConnection.on('stream', async function (stream) {
      setTimeout(closeFunc, personalTime * 1000);
      remoteVideo.get(0).srcObject = stream;
      remoteVideo.get(0).playsInline = true;
      await remoteVideo.get(0).play().catch(console.error);
    });

    mediaConnection.once('close', function () {
      remoteVideo.get(0).srcObject.getTracks().forEach(function (track) { track.stop() });
      remoteVideo.get(0).srcObject = null;
    });

    function closeFunc() {
      mediaConnection.close(true);
      console.log(personalTime)
      ticketOrder += 1
      getPeerId(ticketOrder, lastTicket, personalTime);
    }
  };

  function postPeerId(peerId) {
    let ticketId = $('#js-ticket').attr('value')
    $.ajax({
      url: '/ajax/ticket/post/',
      data: {
        'userPeerId': peerId,
        'ticketId': ticketId,
      },
      dataType: 'json',
    })
      .done(function (data) {
        window.onbeforeunload = onBeforeunloadHandler; // イベント中のページ移動を阻止
        $('#note').modal('hide'); // 注意事項を非表示
        $('#pleaseWaitInner').append('<p>このままお待ちください。</p>');
      }).fail(function () {
        $('#js-join').removeAttr('disabled'); // 「参加する」ボタンを有効化
      });
  }

  // User側のaction
  peer.on('open', function () {
    $('#js-join').click(function () { // onbeforeunloadをトリガーするためにはクリック等の操作が必要
      $('#js-join').attr('disabled', 'disabled'); // 「参加する」ボタンを無効化
      postPeerId(peer.id);
    });
  });

  // host function!!
  // Host側のaction
  $('#js-start').click(function () {
    $('#js-start').remove(); // 「開始する」ボタンを削除
    const lastTicket = $('#js-lastTicket').attr('value')
    const personalTime = $('#js-personalTime').attr('value')
    $('#note').modal('hide'); // 注意事項を非表示
    $('#noteButton').remove(); // 注意事項を表示するボタンを消して
    pleaseWait.remove(); // 「お待ちください」を消して
    $('.remote-video-container').removeClass('d-none'); // remoteVideoを表示する．
    window.onbeforeunload = onBeforeunloadHandler; // イベント中のページ移動を阻止
    getPeerId(1, lastTicket, personalTime)
  })

  function getPeerId(ticketOrder, lastTicket, personalTime) {

    if (ticketOrder <= lastTicket) {
      $.ajax({
        url: '/ajax/ticket/get/',
        data: {
          'eventId': eventId,
          'ticketOrder': ticketOrder,
        },
        dataType: 'json',
      }).done(function (data) {
        if (data.userPeerId != 0) {
          makeCalll(data.userPeerId, ticketOrder, lastTicket, personalTime);
          $('#remoteVideoName').text(data.username);
        } else {
          console.log('skip');
          ticketOrder += 1;
          getPeerId(ticketOrder, lastTicket, personalTime);
        }
      }).fail(() => {
        console.log('Failed to get remote peer id.');
        ticketOrder += 1;
        getPeerId(ticketOrder, lastTicket, personalTime);
      });
    } else {
      window.onbeforeunload = null; // イベント離脱を許可
      let finUrl = '/event/' + eventId + '/finish'
      window.location.href = finUrl;
    }

  }

  // ページ移動を阻止するイベントハンドラ
  var onBeforeunloadHandler = function (e) {
    return 'イベントを中断しますか？';
  };

  // Register callee handler
  // call function
  peer.on('call', function (mediaConnection) {
    mediaConnection.answer(localStream);

    mediaConnection.on('stream', async function (stream) {
      $('#noteButton').remove();
      pleaseWait.remove(); // 「お待ちください」を消して
      $('.remote-video-container').removeClass('d-none'); // remoteVideoを表示する．
      // Render remote stream for callee
      remoteVideo.get(0).srcObject = stream;
      remoteVideo.get(0).playsInline = true;
      await remoteVideo.get(0).play().catch(console.error);
    });

    mediaConnection.once('close', function () {
      remoteVideo.get(0).srcObject.getTracks().forEach(function (track) { track.stop() });
      remoteVideo.get(0).srcObject = null;
      window.onbeforeunload = null; // イベント離脱を許可
      let finUrl = '/event/' + eventId + '/finish'
      window.location.href = finUrl;
    });

  });

  peer.on('error', console.error);
};
document.addEventListener('DOMContentLoaded', videoChat);