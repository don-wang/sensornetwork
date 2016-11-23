var app = angular.module('App',[]);

// Change angular html template tags to avoid conflict with flask
app.config(function($interpolateProvider) {
  $interpolateProvider.startSymbol('[[');
  $interpolateProvider.endSymbol(']]');
});

app.controller('Ctrl', function($scope, socket) {


    // scoket listenters
    socket.on('status', function (data) {
        // application logic ....
        $scope.status = data.msg;
    });

    socket.on('senList', function (data) {
        // application logic ....
        console.log(data);
        d = JSON.parse(data);
        // d = data;
        // var a = d.data.split(",");
        $scope.sensors = d;
        // $scope.counts = Object.keys(d).length;
        // $scope.data.avePre
    });

    // scoket listenters
    // socket.on('push', function (data) {
    //     // application logic ....
    //     d = JSON.parse(data);
    //     // d = data;

    //     // var a = d.data.split(",");
    //     $scope.data = d;
    //     // $scope.data.avePre
    //     console.log(d);
    // });

    $scope.count = function(){
        socket.emit('count');
        return false;
    }
    $scope.clear = function(){
        socket.emit('clear');
        return false;
    }

    $scope.tempToColor = function(temp){
      if (temp<26) {
        return "bg-info";
      } else if (temp > 26 && temp < 29) {
        return "bg-warning";
      } else {
        return "bg-danger";
      }
    }
    $scope.parseData = function(data){
      return(JSON.parse(data));
    }
    $scope.setNamespace = function(sensor){
      newName = document.getElementById(sensor).value;
      socket.emit('newName', {'sensor': sensor, 'newName': newName});
      console.log(sensor, newName);
        // socket.on('push', function (data) {
        // socket.emit('count');
        //     // $scope.data.avePre
        //     console.log(d);
        // });
    }

// PMV


//     //Brightness
//     var winWidth = window.innerWidth;
//     var canvBrightness = document.getElementById("canvBrightness");
//     if(canvBrightness != null){
//     canvBrightness.setAttribute("width", 340 - 60);
//     canvBrightness.setAttribute("height", 120);
//     // canv.setAttribute("style", "margin: 0 10px");
//     var smoothieFlow = new SmoothieChart({
//       grid: { strokeStyle:'white', fillStyle:'black',
//               lineWidth: 1, millisPerLine: 5000, verticalSections: 2, },
//       labels: { fillStyle:'white', fontSize:16 },
//       maxValue:800,
//       minValue: 0
//     });
//     // Data
//     var lineFlow = new TimeSeries();

//     // Add a random value to each line every second
//     setInterval(function() {
//       lineFlow.append(new Date().getTime(), $scope.data.temp);
//       // line2.append(new Date().getTime(), Math.random());
//     }, 1000);

//     // Add to SmoothieChart
//     smoothieFlow.addTimeSeries(lineFlow,
//   { strokeStyle:'rgb(250,250,250)', fillStyle:'rgba(250,250,250, 0.4)', lineWidth:3 });

//     smoothieFlow.streamTo(canvBrightness, 1000);
// }

//
});


app.factory('socket', function ($rootScope) {
  var socket = io.connect('http://' + document.domain + ':' + location.port + '/main');
  return {
    on: function (eventName, callback) {
      socket.on(eventName, function () {
        var args = arguments;
        $rootScope.$apply(function () {
          callback.apply(socket, args);
        });
      });
    },
    emit: function (eventName, data, callback) {
      socket.emit(eventName, data, function () {
        var args = arguments;
        $rootScope.$apply(function () {
          if (callback) {
            callback.apply(socket, args);
          }
        });
      })
    }
  };
});

