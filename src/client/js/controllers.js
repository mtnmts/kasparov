

creatorApp.controller('ApplicationCtrl' ,
  function($scope){

  });


creatorApp.controller('NewWebsiteCtrl', function($scope, $location,flash,  Restangular) {
      $scope.base = Restangular.all('/api/website');
      $scope.actions = [
        {id : 1, text: 'Update & Upgrade (Recommended)'},
        {id : 2, text: 'nginx (Web Server)'},
        {id : 3, text: 'mySQL'},
        {id : 4, text: 'PHP'},
        {id : 5, text: 'Wordpress'}
      ]
      $scope.submitNewWebsiteAnother = function (website_form) {
        flash("Added Website!");
        $scope.base.post(website_form);
        console.log(website_form);
      }

      $scope.submitNewWebsite = function (website_form) {
        console.log(website_form);
        $scope.base.post(website_form);
        flash("Added Website!");
        $location.path('/home');
      }
   
     
  });

creatorApp.controller('HomeCtrl', function($scope, $location, Restangular) {
      $scope.base = Restangular.all('/api/website');
      //$scope.websites = {'ip' : '0.0.0.0', 'pass' : '1234', 'user': 'root'};
      $scope.base.getList().then(function(webs){
        $scope.websites = webs;
      });
      $scope.install = function(e) {
        install_id = e.target.attributes['data-id'].value;
        console.log("Recieved install request for ID ", install_id);
        $location.path('/install/' + install_id);
      }
      
  });


function installer_message(msg, $scope) {
  obj = angular.fromJson(msg.data);
  console.log(msg.data)
  if(obj.type == "LOG_MAIN") {
    $scope.main_log.push({"data" : obj.payload, "class" : "list-group-item-info"})
  }
  if(obj.type == "LOG_ERROR"){
    $scope.main_log.push({"data" : obj.payload, "class" : "list-group-item-danger"})
  }
   if(obj.type == "LOG_INFO"){
    $scope.main_log.push({"data" : obj.payload, "class" : "list-group-item-success"})
  }
  if(obj.type == "LOG_SECONDARY"){
    $scope.secondary_log = obj.payload + "\n" + $scope.secondary_log;
  }

  if(obj.type == "PROGRESS_REPORT"){
    console.log("Updating progress")
    $scope.progress_prec = obj.payload
  }

}

function install_server(msg) {
  msg['type'] = 'INSTALL_CMD'
  return msg
}
creatorApp.controller('InstallCtrl', function($scope,$websocket, $route, $routeParams, Restangular) {
        $scope.install_id = $route.current.params.installId;
        r = Restangular.one('/api/website/' +  $scope.install_id).get();
        $scope.progress_prec = "5";
        $scope.main_log = [];
        $scope.secondary_log = "";
        r.then(function(site) {
          $scope.site = site;
          console.log("Successfully loaded site installer");
          console.log("Opening websocket")

          var dataStream = $websocket('ws://127.0.0.1:9190');
          console.log("Sending data")
          dataStream.send(install_server($scope.site));
          setInterval(function(){dataStream.send({"ping":"pong"})}, 2000);
          dataStream.onMessage(function(msg) { installer_message(msg, $scope); });


        });
      
          
        

      //$scope.install_id = $scope.params['install_id'];     
  });



creatorApp.controller('configureCtrl', function($scope,$websocket, $route, $routeParams, Restangular) {
        $scope.site_id = $route.current.params.siteId;     
  });


creatorApp.config(['$routeProvider',
  function($routeProvider) {
    $routeProvider.
      when('/new_website', {
        templateUrl: 'static/partials/new_website.html',
        controller: 'NewWebsiteCtrl'
      }).when('/home',
        {
          templateUrl: 'static/partials/home.html',
          controller: 'HomeCtrl'
        }).when('/install/:installId',
        {
          templateUrl: 'static/partials/install.html',
          controller: 'InstallCtrl'
        }).when('/configure/:siteId',
        {
          templateUrl: 'static/partials/configure.html',
          controller: 'configureCtrl'
        }).otherwise({
        redirectTo: '/home'
      });
  }]);