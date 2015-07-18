function applicationCtrlFn($scope) {

}



function newWebsiteCtrlFn($scope) {

}



creatorApp.controller('ApplicationCtrl' ,
  function($scope){

  });


creatorApp.controller('NewWebsiteCtrl', function($scope, $location,flash,  Restangular) {
      $scope.base = Restangular.all('/api/website');
      $scope.submitNewWebsiteAnother = function (website_form) {
        flash("Added Website!");
        $scope.base.post(website_form);
      }

      $scope.submitNewWebsite = function (website_form) {
        console.log(website_form);
        $scope.base.post(website_form);
        flash("Added Website!");
        $location.path('/home');
      }
      $scope.submitInstall = function (website_form) {
        console.log(website_form);
        $scope.base.post(website_form).then(function(e) {
          $scope.id = e.server_id;
          flash("Installing Directly!");
          $location.path('/install/' + $scope.id);
          
        
        });
      }
     
  });

creatorApp.controller('HomeCtrl', function($scope, $location, Restangular) {
      $scope.base = Restangular.all('/api/website');
      $scope.websites = {'ip' : '0.0.0.0', 'pass' : '1234', 'user': 'root'};
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
  console.log(msg);  
}

function install_server(server_id) {
  return {type : 'INSTALL_CMD', 'server_id' : server_id}
}
creatorApp.controller('InstallCtrl', function($scope,$websocket, $route, $routeParams, Restangular) {
        $scope.install_id = $route.current.params.installId;
        r = $scope.base = Restangular.one('/api/website/' +  $scope.install_id).get();
        r.then(function(site) {
          $scope.site = site;
          console.log("Successfully loaded site installer");
          console.log("Opening websocket")

          var dataStream = $websocket('ws://127.0.0.1:9190');
          console.log("Sending data")
          dataStream.send(install_server($scope.install_id));
          dataStream.onMessage(function(msg) { installer_msg(msg, $scope); });


        });
      
          
        

      //$scope.install_id = $scope.params['install_id'];     
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
        }).otherwise({
        redirectTo: '/home'
      });
  }]);