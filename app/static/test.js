var app = angular.module('App',[]);

// Change angular html template tags to avoid conflict with flask
app.config(function($interpolateProvider) {
  $interpolateProvider.startSymbol('[[');
  $interpolateProvider.endSymbol(']]');
});

app.controller('Ctrl', function($scope) {
$scope.namespace = "main";
$scope.result = "main";
socket = io.connect('http://' + document.domain + ':' + location.port + '/' + $scope.namespace);
    // socket.on('push', function (data) {
    //     // application logic ....
    //     d = JSON.parse(data);
    //     // d = data;
    //     // var a = d.data.split(",");
    //     $scope.data = d;
    //     // $scope.data.avePre
    //     console.log(d);
    // });
    // // scoket listenters
    // socket.on('status', function (data) {
    //     // application logic ....
    //     $scope.status = data.msg;
    // });



    $scope.changeNamespace = function(namespace){
        socket.disconnect();
        // socket.socket.disconnect()
        socket = io.connect('http://' + document.domain + ':' + location.port + '/' + namespace);
        console.log("Now listening to " + namespace);
        console.log('http://' + document.domain + ':' + location.port + '/' + namespace);
        $scope.result = namespace;
        socket.on('senList', function (data) {
            // application logic ....

            d = JSON.parse(data);
            // d = data;
            // var a = d.data.split(",");
            $scope.data = d;
            // $scope.data.avePre
            console.log(data);
        });
    }


//
});


// app.factory('socket', function ($rootScope) {
//   var socket = io.connect('http://' + document.domain + ':' + location.port + '/D74CF85F2848');
//   return {
//     on: function (eventName, callback) {
//       socket.on(eventName, function () {
//         var args = arguments;
//         $rootScope.$apply(function () {
//           callback.apply(socket, args);
//         });
//       });
//     },
//     emit: function (eventName, data, callback) {
//       socket.emit(eventName, data, function () {
//         var args = arguments;
//         $rootScope.$apply(function () {
//           if (callback) {
//             callback.apply(socket, args);
//           }
//         });
//       })
//     }
//   };
// });

