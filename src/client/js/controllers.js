function applicationCtrlFn($scope) {

}



function newWebsiteCtrlFn($scope) {

}



creatorApp.controller('ApplicationCtrl' ,
  function($scope){

  });


creatorApp.controller('NewWebsiteCtrl', function($scope, $location, Restangular) {
      $scope.base = Restangular.all('/api/website');
      $scope.submitNewWebsiteAnother = function (website_form) {
        console.log(website_form);
        $scope.base.post(website_form);
      }
      $scope.submitNewWebsite = function (website_form) {
        console.log(website_form);
        $scope.base.post(website_form);
        $location.path('/home');
      }
  });

creatorApp.controller('HomeCtrl', function($scope, Restangular) {
      $scope.base = Restangular.all('/api/website');
      $scope.websites = {'ip' : '0.0.0.0', 'pass' : '1234', 'user': 'root'};
      $scope.base.getList().then(function(webs){
        $scope.websites = webs;
      })
      
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
        }).
      otherwise({
        redirectTo: '/home'
      });
  }]);