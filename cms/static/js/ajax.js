const Peer = window.Peer;
// jquery
(async function main() {
  // videochat
  const localVideo = $("#js-local-stream");
  const localId = $("#js-local-id");
  const callTrigger = $("#js-call-trigger");
  const closeTrigger = $("#js-close-trigger");
  const remoteVideo = $("#js-remote-stream");
  const remoteId = $("#js-remote-id");
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

  function fetchRemoteId() {
    if($("#js-user").length){
      console.log("is_user")
      var remote_id = $("#js-local-id").text()
      return remote_id
    }
  }

  function makeCalll(remotePeerId){
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
    }

    // Todo:4000を変数（personal time）にする
    // 4病後に回線を切断する．
    setTimeout(closeFunc, 4000);

    // closeTrigger.on('click', () => mediaConnection.close(true));
  };

  peer.on("open",function(){
    localId.text(peer.id)
    var remote_id = fetchRemoteId();
    console.log("suc");
    console.log(remote_id)
  });

  // host function!!
  $("#js-start").click(function(){
    let ticketOrder = $("#ticketOticketOrder").attr("value");
    for(var i=1; i <1; i ++){
      getPeerId(ticketOrder);
    }
  })  


  function getPeerId(ticketOrder) {
    let peerId = fetchRemoteId();
    $.ajax({
      url: '/ajax/ticket/get',
      data: {
        'userPeerId': peerId,
        'ticketOrder':  ticketOrder,
      },
      dataType: 'json',
      success: function(data){
        makeCalll(data.userPeerId)
        // if ( nowOrder == data.ticketOrder){
        //   つなげる
        //   console.log(data)
        // }else{
        //   待ち時間，人数を変える
        // }
      }
    })
  }


  function postPeerId(){
    let peerId = fetchRemoteId();
    $.ajax({
      url: '/ajax/ticket/post',
      data: {
        'userPeerId': peerId,
        'ticketId': ticketId,
      },
      dataType: 'json',
      success: function(data){

      }
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