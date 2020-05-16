// const Peer = window.Peer;

(async function main() {

  // timer
  var timer = document.getElementById('timer');
  var reset = document.getElementById('reset');
  var start = document.getElementById('start');
  var timerId;

  var startTime;
  var timeLeft;
  // TODO: ミリ秒，イベントごとに時間を変える
  var timeToCountDown = 4 * 1000;

  function updateTimer(t) {
    var d = new Date(t);
    var s = d.getSeconds();
    timer.textContent = '残り' + s + '秒';
  }

  function  countDown() {
    timerId = setTimeout(function() {
      var elapsedTime = Date.now()
      timeLeft = timeToCountDown - (Date.now() - startTime);
      if(timeLeft < 0){
        clearTimeout(timerId);
        timeLeft = 0;
        timeToCountDown = 0;
        updateTimer(timeLeft);
        return;
      }

      updateTimer(timeLeft);
      countDown();
    }, 10);
  }

  start.addEventListener('click', function () {
    startTime = Date.now();
    countDown();
  });






  // videochat
  const localVideo = document.getElementById('js-local-stream');
  const localId = document.getElementById('js-local-id');
  const callTrigger = document.getElementById('js-call-trigger');
  const closeTrigger = document.getElementById('js-close-trigger');
  const remoteVideo = document.getElementById('js-remote-stream');
  const remoteId = document.getElementById('js-remote-id');
  const meta = document.getElementById('js-meta');
  const sdkSrc = document.querySelector('script[src*=skyway]');

  meta.innerText = `
    UA: ${navigator.userAgent}
    SDK: ${sdkSrc ? sdkSrc.src : 'unknown'}
  `.trim();

  const localStream = await navigator.mediaDevices
    .getUserMedia({
      audio: true,
      video: true,
    })
    .catch(console.error);

  // Render local stream
  localVideo.muted = true;
  localVideo.srcObject = localStream;
  localVideo.playsInline = true;
  await localVideo.play().catch(console.error);

  // const peer = new Peer({
  //   key: '5dd945ee-88eb-4e9c-9d78-165a2e17a4d2',
  //   debug: 3,
  // });

  // Register caller handler
  callTrigger.addEventListener('click', () => {
    // Note that you need to ensure the peer has connected to signaling server
    // before using methods of peer instance.
    if (!peer.open) {
      return;
    }

    const mediaConnection = peer.call(remoteId.value, localStream);

    mediaConnection.on('stream', async stream => {
      // Render remote stream for caller
      remoteVideo.srcObject = stream;
      remoteVideo.playsInline = true;
      await remoteVideo.play().catch(console.error);
    });

    mediaConnection.once('close', () => {
      remoteVideo.srcObject.getTracks().forEach(track => track.stop());
      remoteVideo.srcObject = null;
    });

    closeTrigger.addEventListener('click', () => mediaConnection.close(true));
  });

  peer.once('open', id => (localId.textContent = id));

  // Register callee handler
  peer.on('call', mediaConnection => {
    mediaConnection.answer(localStream);

    mediaConnection.on('stream', async stream => {
      // Render remote stream for callee
      remoteVideo.srcObject = stream;
      remoteVideo.playsInline = true;
      await remoteVideo.play().catch(console.error);
    });

    mediaConnection.once('close', () => {
      remoteVideo.srcObject.getTracks().forEach(track => track.stop());
      remoteVideo.srcObject = null;
    });

    closeTrigger.addEventListener('click', () => mediaConnection.close(true));
  });

  peer.on('error', console.error);
})();



























// window.onload = function(){


//   // カメラ映像取得
//   const localStream = await  navigator.mediaDevices.getUserMedia({ video: true, audio: true })
//     .then(stream => {
//       // 成功時にvideo要素にカメラ映像をセットし、再生
//       const videoElm = document.getElementById('my-video')
//       videoElm.srcObject = stream;
//       videoElm.play();
//       // 着信時に相手にカメラ映像を返せるように、グローバル変数に保存しておく
//       localStream = stream;
//     }).catch(error => {
//       // 失敗時にはエラーログを出力
//       console.error('mediaDevice.getUserMedia() error:', error);
//       return;
//     });

//   // Keyを環境変数にする
//   const peer = new Peer({
//     key: '5dd945ee-88eb-4e9c-9d78-165a2e17a4d2',
//     debug: 3
//   });

//   //PeerID取得
//   // peer.on('open', id => {});
//   // シグナルサーバへ正常に接続できたときのイベント
//   peer.on('open', () => {
//     document.getElementById('my-id').textContent = peer.id;
//   });

//   document.getElementById('make-call').onclick = () => {
//     const theirID = document.getElementById('their-id').value;
//     // 自身のlocalStreamを設定して
//     const mediaConnection = peer.call(theirID, localStream, {
//       metadata: {
//         // userのオーダー番号を渡す
//       }
//     });
//     setEventListener(mediaConnection);
//   };

//   document.getElementById('close-call').onclick = () => {
//     const theirID = document.getElementById('their-id').value;
//     // const mediaConnection = peer.call(theirID, localStream, {
//     // });
//     peer.disconnect(theirID);
//   };

//   // イベントリスナを設置する関数
//   // 相手の映像画面を表示するため
//   const setEventListener = mediaConnection => {
//     // mediaConnectionのonメソッドにて，相手の映像を取得したときに発生するstreamイベントのリスナを用意する
//     mediaConnection.on('stream', async stream => {
//       // video要素にカメラ映像をセットして再生

//       const videoElm = document.getElementById('their-video')
//       videoElm.srcObject = stream;
//       await videoElm.play().catch(console.error);
//     });


//     mediaConnection.once('close', () => {
//       remoteVideo.srcObject.getTracks().forEach(track => track.stop());
//       remoteVideo.srcObject = null;
//     });

//     closeTrigger.addEventListener('click', () => mediaConnection.close(true));
//   }


//   //着信処理
//   //相手から接続要求が来た時に発火
//   // 接続先のPeerからメディアチャネル（音声・映像）の映像を受信したときのイベント
//   peer.on('call', mediaConnection => {
//     mediaConnection.answer(localStream);
//     setEventListener(mediaConnection);
//   });

//   const sec = 5;
//   peer.on('expiresin', sec => {

//   });

// }

