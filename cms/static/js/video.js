class CountDown {
  constructor(countDownFrom) {
    this.countDownFrom = this.remainingTime = countDownFrom;
    this.countDownElm = document.getElementById('countDown');
    this.timerId = null;
  }
  set() {
    this.countDownElm.classList.remove('d-none');
    this.countDownElm.innerText = this.remainingTime;
    this.remainingTime--;
    this.timerId = setInterval(() => this.timer(), 1000);
    setTimeout(() => this.clear(), this.countDownFrom * 1000);
  }
  timer() {
    this.countDownElm.innerText = this.remainingTime;
    this.remainingTime--;
  }
  clear() {
    clearInterval(this.timerId);
    this.countDownElm.classList.add('d-none');
  }
}

var videoChat = async () => {
  const localVideo = document.getElementById('localVideo');
  const remoteVideo = document.getElementById('remoteVideo');
  const pleaseWait = $('#pleaseWait');
  const $notes = $('#notes');
  const joinBtn = document.getElementById('js-join');

  const countDownFrom = 5;
  const data = JSON.parse(document.getElementById('js-data').textContent);
  const eventId = data.eventId;
  const personalTime = data.personalTime;
  const finUrl = '/event/' + eventId + '/finish';

  $notes.modal('show'); // 注意事項を表示

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
    .catch(error => {
      console.error(error);
      document.getElementById('mediaNote').classList.remove('d-none'); // カメラとマイクをオンにする注意文を表示
    });

  // Render local stream
  localVideo.muted = true;
  localVideo.srcObject = localStream;
  localVideo.playsInline = true;
  await localVideo.play().catch(console.error);

  const peer = new Peer({
    key: '889cd639-6a9e-4947-b168-35ad15fb44cb',
  });

  if (data.host) {
    // host function!!
    // Host側のaction
    $('#js-start').click(() => {
      $('#js-start').remove(); // 「開始する」ボタンを削除
      $notes.modal('hide'); // 注意事項を非表示
      $('#notesButton').remove(); // 注意事項を表示するボタンを消して
      pleaseWait.remove(); // 「お待ちください」を消して
      $('.remote-video-container').removeClass('d-none'); // remoteVideoを表示する．
      window.onbeforeunload = onBeforeunloadHandler; // イベント中のページ移動を阻止
      getPeerId(1);
    });
  } else {
    // Fan側のaction
    peer.on('open', () => {
      joinBtn.removeAttribute('disabled'); // 「参加する」ボタンを有効化
      joinBtn.addEventListener('click', () => { // onbeforeunloadをトリガーするためにはクリック等の操作が必要
        joinBtn.setAttribute('disabled', 'disabled'); // 「参加する」ボタンを無効化
        postPeerId(peer.id);
      }, false);
    });
    // Register callee handler
    // call function
    peer.on('call', mediaConnection => {
      mediaConnection.answer(localStream);

      mediaConnection.on('stream', async stream => {
        setTimeout(() => new CountDown(countDownFrom).set(), (personalTime - countDownFrom) * 1000);
        $('#notesButton').remove();
        pleaseWait.remove(); // 「お待ちください」を消して
        $('.remote-video-container').removeClass('d-none'); // remoteVideoを表示する．
        // Render remote stream for callee
        remoteVideo.srcObject = stream;
        remoteVideo.playsInline = true;
        await remoteVideo.play().catch(console.error);
      });

      mediaConnection.once('close', () => {
        remoteVideo.srcObject.getTracks().forEach(track => track.stop());
        remoteVideo.srcObject = null;
        window.onbeforeunload = null; // イベント離脱を許可
        window.location.href = finUrl;
      });
    });
  }

  peer.on('error', console.error);

  // hostがfanにcall
  function makeCall(remotePeerId, ticketOrder) {
    if (!peer.open) {
      return;
    }

    function closeFunc() {
      mediaConnection.close(true);
      ticketOrder += 1;
      getPeerId(ticketOrder);
    }

    const mediaConnection = peer.call(remotePeerId, localStream);

    mediaConnection.on('stream', async stream => {
      setTimeout(closeFunc, personalTime * 1000);
      setTimeout(() => new CountDown(countDownFrom).set(), (personalTime - countDownFrom) * 1000);
      remoteVideo.srcObject = stream;
      remoteVideo.playsInline = true;
      await remoteVideo.play().catch(console.error);
    });

    mediaConnection.once('close', () => {
      remoteVideo.srcObject.getTracks().forEach(track => track.stop());
      remoteVideo.srcObject = null;
    });
  };

  // hostがfanのpeerIdをget
  function getPeerId(ticketOrder) {
    if (ticketOrder <= data.lastTicket) {
      $.ajax({
        url: '/ajax/ticket/get/',
        data: {
          'eventId': eventId,
          'ticketOrder': ticketOrder,
        },
        dataType: 'json',
      }).done(resp => {
        if (resp.userPeerId != 0) {
          makeCall(resp.userPeerId, ticketOrder);
          $('#remoteVideoName').text(resp.username);
        } else {
          console.log('skip');
          ticketOrder += 1;
          getPeerId(ticketOrder);
        }
      }).fail(() => {
        console.log('Failed to get remote peer id.');
        ticketOrder += 1;
        getPeerId(ticketOrder);
      });
    } else {
      window.onbeforeunload = null; // イベント離脱を許可
      window.location.href = finUrl;
    }
  }

  // fanがpeerIdをpost
  function postPeerId(peerId) {
    $.ajax({
      url: '/ajax/ticket/post/',
      data: {
        'userPeerId': peerId,
        'ticketId': data.ticketId,
      },
      dataType: 'json',
    }).done(resp => {
      window.onbeforeunload = onBeforeunloadHandler; // イベント中のページ移動を阻止
      $notes.modal('hide'); // 注意事項を非表示
      $('#pleaseWaitInner').append(
        `<p>あなたの順番は全体の${data.order}番目です。<br>このままお待ちください。</p>
        <div class="spinner-border" role="status"></div>`
        );
    }).fail(() => {
      joinBtn.removeAttribute('disabled'); // 「参加する」ボタンを有効化
    });
  }

  // ページ移動を阻止するイベントハンドラ
  function onBeforeunloadHandler(event) {
    return 'イベントを中断しますか？';
  }
};
document.addEventListener('DOMContentLoaded', videoChat, false);