<?php
namespace App;
use App\View\View;

class Router {
    private $router;
    public function __construct(){
        $_ENV['DOMAIN'] = getenv('DOMAIN');
        $_ENV['API_UID'] = getenv('API_UID');
        $_ENV['API_SECRET'] = getenv('API_SECRET');
        $_ENV['MYSQL_USER'] = getenv('MYSQL_USER');
        $_ENV['MYSQL_PASSWORD'] = getenv('MYSQL_PASSWORD');
        $_ENV['MYSQL_DATABASE'] = getenv('MYSQL_DATABASE');

        if (
            $_ENV['DOMAIN'] == false ||
            $_ENV['API_UID'] == false ||
            $_ENV['API_SECRET'] == false ||
            $_ENV['MYSQL_USER'] == false ||
            $_ENV['MYSQL_PASSWORD'] == false ||
            $_ENV['MYSQL_DATABASE'] == false
        )
        {
            View::generatePage(500, 'code 501');
            exit;
        }
        $this->router = new \AltoRouter();
        $this->router->addMatchTypes(['word'=>'[A-Za-z]++']);
    }
    private function __clone () {}
    public function get(string $path, $callable, ?string $name = null) {
        $this->router->map('GET', $path, $callable, $name);
        return $this;
    }
    public function post(string $path, $callable, ?string $name = null) {
        $this->router->map('POST', $path, $callable, $name);
        return $this;
    }
    public function run() {
        $match = $this->router->match();
        if($match !== null && $match !== false) {
            if(is_string($match['target']) && preg_match('/[a-z]+#[a-w]\w*/i', $match['target'] )) {
                $params = explode('#', $match['target']);
                $controller = "App\\Controller\\" . $params[0] . "Controller";
                $controller = new $controller();
                return call_user_func_array([$controller, $params[1]], $match['params']);
            } else if (is_string($match['target'])) {
                echo $match['target'];
            } else {
                return call_user_func_array($match['target'], $match['params']);
            }
        } else {
            View::generatePage(404, 'sorry ;)');
        }
    }
    public function generate($routeName, array $params = []) {
        return $this->router->generate($routeName, $params);
    }
}
