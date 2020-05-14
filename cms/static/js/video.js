window.onload = function(){
  let localStream;

  // カメラ映像取得
  navigator.mediaDevices.getUserMedia({ video: true, audio: true })
    .then(stream => {
      // 成功時にvideo要素にカメラ映像をセットし、再生
      const videoElm = document.getElementById('my-video')
      videoElm.srcObject = stream;
      videoElm.play();
      // 着信時に相手にカメラ映像を返せるように、グローバル変数に保存しておく
      localStream = stream;
    }).catch(error => {
      // 失敗時にはエラーログを出力
      console.error('mediaDevice.getUserMedia() error:', error);
      return;
    });

  // Keyを環境変数にする
  const peer = new Peer({
    key: '5dd945ee-88eb-4e9c-9d78-165a2e17a4d2',
    debug: 3
  });

  //PeerID取得
  peer.on('open', () => {
    document.getElementById('my-id').textContent = peer.id;
  });

  document.getElementById('make-call').onclick = () => {
    const theirID = document.getElementById('their-id').value;
    const mediaConnection = peer.call(theirID, localStream);
    setEventListener(mediaConnection);
  };

  // イベントリスナを設置する関数
  const setEventListener = mediaConnection => {
    mediaConnection.on('stream', stream => {
      // video要素にカメラ映像をセットして再生
      const videoElm = document.getElementById('their-video')
      videoElm.srcObject = stream;
      videoElm.play();
    });
  }

  //着信処理
  //相手から接続要求が来た時に発火
  peer.on('call', mediaConnection => {
    mediaConnection.answer(localStream);
    setEventListener(mediaConnection);
  });

  peer.on('close', ()=> {
    alert('お疲れさまでした．')
  });

}

