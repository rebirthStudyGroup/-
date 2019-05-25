
function titleTypeChange() {
    var titleType = document.getElementById("title-type");
    var clalenderType =  document.getElementById("calender-type").value;
    if (clalenderType == 0) {
        // モーダルだし分け
        // 抽選フォーム
        titleType.textContent = "抽選エントリーフォーム"; 
      } else {
        titleType.textContent = "予約・二次予約フォーム";
      } 
  }
$(document).ready(function() {

  // 数か月先をとるプロトタイプ　ネットに落ちてた。
  // http://www.is-p.cc/web-skill/javascript-%E4%B8%80%E3%83%B6%E6%9C%88%E5%BE%8C%EF%BC%88n%E3%83%B5%E6%9C%88%E5%BE%8C%EF%BC%89%E3%82%92%E5%8F%96%E5%BE%97%E3%81%99%E3%82%8B%E9%96%A2%E6%95%B0/1159
  Date.prototype.addMonth = function( m ) {
    var d = new Date( this );
    var dates = d.getDate();
    var years = Math.floor( m / 12 );
    var months = m - ( years * 12 );
    if( years ) d.setFullYear( d.getFullYear() + years );
    if( months ) d.setMonth( d.getMonth() + months );
    if( dates == 1 ) {
        d.setDate( 0 );
    } else {
        d.setDate( d.getDate() - 1 );
    }
    return d;
}
  //eventデータ
  var title = "hogeddd";
  var dt = new Date();
  // addMonth関数を使う
  var prem = dt.addMonth( 3 );
  var y = dt.getFullYear();
  var m = ("00" + (dt.getMonth() + 1)).slice(-2);
  var d = ("00" + dt.getDate()).slice(-2);
  i = parseInt(d);
  var nowDate = [];
  for (i = 1; i < 32; i++) {
    nowDate = y + "-" + m + "-" + i;
    console.log(nowDate);
  }

  

  // カレンダーの設定
  $("#calendar").fullCalendar({
    // new Date();
    defaultDate: prem,
    height: 550,
    lang: "ja",
    selectable: true,
    selectHelper: true,

    // select: function(start, end) {
    // var title = prompt("予定タイトル:");
    // var eventData;
    // if (title) {
    //         eventData = {
    //                 title: title,
    //                 start: start,
    //                 end: end
    //         };
    //         $('#calendar').fullCalendar('renderEvent', eventData, true); // stick? = true
    // }
    // $('#calendar').fullCalendar('unselect');
    // },
    editable: true,
    eventLimit: true,
    success: function(calEvent) {
      $("#calendar").fullCalendar("removeEvents");
      $("#calendar").fullCalendar("addEventSource", calEvent);
    },

    events: [
      {
        title: "タイトル",
        start: "2019-05-25",
      }
    ],

    eventClick: function(calEvent, jsEvent, view) {},
    dayClick: function(date, jsEvent, view) {
      // 編集ボタンと削除ボタン、ついでに閉じるボタンのHTML要素を追加

      var firstLotteryDay = date.format();
      var datepicker_start = document.getElementById("datepicker_start");
      datepicker_start.value = firstLotteryDay;

      var datepicker_start2 = document.getElementById("datepicker_start2");
      datepicker_start2.value = firstLotteryDay;
      var clalenderType =  document.getElementById("calender-type").value;
      if (clalenderType == 0) {
        // モーダルだし分け
        $("#calendarModal").modal(); // モーダル着火
      } else {
        $("#calendarModal2").modal(); // モーダル着火
      }  
    }
  });
});
