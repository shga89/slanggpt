// static/js/script.js

// static/js/script.js (또는 index.html의 <script> 태그 안에)

function handleEnter(event) {
  if (event.key === "Enter" && !event.shiftKey) {
    // Shift 키가 눌리지 않은 상태에서 Enter 키가 눌렸을 때
    event.preventDefault(); // 기본 Enter 키 동작(줄바꿈) 방지
    document.querySelector(".chat-input-area form").submit(); // 폼 전송
  }
}

document.addEventListener('DOMContentLoaded', function() { // DOMContentLoaded 이벤트 리스너 사용
    // textarea 요소에 이벤트 리스너 추가
    var textarea = document.querySelector(".chat-input-area textarea");
    if (textarea) { // textarea 요소가 존재하는지 확인
        textarea.addEventListener("keydown", handleEnter);
    }

      var termsAgreed = getCookie("terms_agreed");
      var showPopup = document.getElementById('termsModal');

      if (showPopup && !termsAgreed) {
        showPopup.style.display = 'block';
      }

        scrollToBottom();

});


function closeModal() {
    document.getElementById('termsModal').style.display = 'none';
}

// 페이지 로드 시 팝업 확인 (쿠키 기반)
window.onload = function() {
  var termsAgreed = getCookie("terms_agreed");
  var showPopup = document.getElementById('termsModal'); // 팝업 요소가 있는지 확인
  if (showPopup && !termsAgreed) {
    showPopup.style.display = 'block';
  }
};

function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length == 2) return parts.pop().split(";").shift();
}

function scrollToBottom() {
    var chatHistoryContainer = document.getElementById("chat-history-container");
    chatHistoryContainer.scrollTop = chatHistoryContainer.scrollHeight;
}

// 페이지 로드 시 스크롤
window.onload = function() {
  var termsAgreed = getCookie("terms_agreed");
  var showPopup = document.getElementById('termsModal'); // 팝업 요소가 있는지 확인

  if (showPopup && !termsAgreed) {
    showPopup.style.display = 'block';
  }
    scrollToBottom(); // 페이지 로드 시 스크롤
};

// 새 메시지가 추가될 때마다 스크롤 (AJAX를 사용하는 경우)
// 이 부분은 form submit 이후에 호출되도록 수정해야 합니다.
// 예: Flask의 경우 form.validate_on_submit() 블록 안에서,
//     db.session.commit() 호출 *후*에 scrollToBottom() 호출
