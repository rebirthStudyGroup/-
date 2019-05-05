$(document).ready(function() {
  //eventデータ
  var title = "hogeddd";
  var dt = new Date();
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
        title: title,
        start: nowDate[i]
      }
    ],

    eventClick: function(calEvent, jsEvent, view) {},
    dayClick: function(date, jsEvent, view) {
      // 編集ボタンと削除ボタン、ついでに閉じるボタンのHTML要素を追加

      var firstLotteryDay = date.format();
      var datepicker_start = document.getElementById("datepicker_start");
      datepicker_start.value = firstLotteryDay;

      $("#calendarModal").modal(); // モーダル着火
    }
  });
});
