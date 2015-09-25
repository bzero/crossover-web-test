var myapp = angular.module('myapp', ['ngRoute']);

// fix jinja2 errors 

myapp.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{[');
  $interpolateProvider.endSymbol(']}');
}]);

myapp.controller('changelistController', ['$scope', '$http', '$timeout', function($scope, $http, $timeout) {
	$scope.items = [];
	$scope.errorMsg = null;
	
	$scope.getItems = function() {
		$http.post('/changelist').then(function(response) {
			$scope.items = response.data.changelist;
		  }, function(response) {
			$scope.errorMsg = response;
		  });
	};
	$scope.notImplemented = function() {
		$scope.errorMsg = 'feature is not yeat implemented';
	};
	$scope.cron = function() {
		$timeout(function() {
			$scope.getItems();
			$scope.$apply();
			$scope.cron();
		}, 30000);
	};
	$scope.expand = function(item) {
		if (item.state != 'pending' && item.state != 'running') {
			$scope.errorMsg = null;
			$scope.items.forEach(function(i) {
				if (i != item) {
					i.show = false;
				}
			});
			if (item.show) {
				item.show = false;
			} else {
				item.show = true;
			}
		}
	};
	$scope.getItems();
	$scope.cron();
}]);