const Peer = window.Peer;
// jquery
(async function main() {
  // videochat
  const localVideo = $("#localVideo");
  const localId = $("#js-local-id");
  const closeTrigger = $("#js-close-trigger");
  const remoteVideo = $("#remoteVideo");
  const meta = $("#js-meta");
  const sdkSrc = document.querySelector("script[src*=skyway]");

  meta.innerText = `
    UA: ${navigator.userAgent}
    SDK: ${sdkSrc ? sdkSrc.src : "unknown"}
  `.trim();

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
    key: "889cd639-6a9e-4947-b168-35ad15fb44cb",
    debug: 3,
  });

  function makeCalll(remotePeerId, ticketOrder){
    if (!peer.open) {
      return;
    }

    const mediaConnection = peer.call(remotePeerId, localStream);

    mediaConnection.on("stream", async function(stream){
      remoteVideo.get(0).srcObject = stream;
      remoteVideo.get(0).playsInline = true;
      await remoteVideo.get(0).play().catch(console.error);
    });

    mediaConnection.once("close", function(){
      remoteVideo.get(0).srcObject.getTracks().forEach(function(track){track.stop()});
      remoteVideo.get(0).srcObject = null;
      console.log("Hello.");
    });

    function closeFunc() {
      mediaConnection.close(true);
      ticketOrder += 1
      getPeerId(ticketOrder);
    }

    // Todo:4000を変数（personal time）にする
    // 4病後に回線を切断する．
    setTimeout(closeFunc, 4000);
  };

  function postPeerId(peerId) {
    let ticketId = $("#js-ticket").attr("value")
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
  peer.on("open", function () {
    if ($("#js-user").length) {
      postPeerId(peer.id);
    }
  });

  // host function!!
  // Host側のaction
  $("#js-start").click(function(){
    getPeerId(1)
  })

  function getPeerId(ticketOrder) {
    let eventId = $("#js-host").attr("value");
    $.ajax({
      url: '/ajax/ticket/get',
      data: {
        'eventId': eventId,
        'ticketOrder': ticketOrder,
      },
      dataType: 'json',
    }).done(function (data) {
      makeCalll(data.userPeerId, ticketOrder)
    })
  }

  // Register callee handler
  peer.on("call", function(mediaConnection){
    mediaConnection.answer(localStream);

    mediaConnection.on("stream", async function(stream){
      // Render remote stream for callee
      remoteVideo.get(0).srcObject = stream;
      remoteVideo.get(0).playsInline = true;
      await remoteVideo.get(0).play().catch(console.error);
    });

    mediaConnection.once("close", function(){
      remoteVideo.get(0).srcObject.getTracks().forEach(function(track){track.stop()});
      remoteVideo.get(0).srcObject = null;
    });

    closeTrigger.on("click", function(){mediaConnection.close(true)});
  });

  peer.on("error", console.error);
})();