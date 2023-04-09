<?php
namespace App\Controller;

use App\Model\Manager;
use App\View\View;
use PDO;
use Rexlabs\HyperHttp\Hyper;

class MainController {

	public function getHome() {
		return View::generatePage(200, 'index');
	}

	public function getOauth() {
		if (!isset($_GET['code']))
			return View::generatePage(400, 'code 001');
		session_start();
		$_SESSION['code'] = $_GET['code'];
		$data['url_intra'] = 'https://api.intra.42.fr/oauth/authorize?client_id='.$_ENV['API_UID'].'&redirect_uri='.$_ENV['DOMAIN'].'%2Fconnected&response_type=code';
		return View::generatePage(200, 'api', $data);
	}

	public function getConnectDiscord() {
		session_start();
		if (!isset($_GET['code']) || !isset($_SESSION['code'])) 
			return View::generatePage(400, 'code 002');
		$codeIntra = $_GET['code'];
		$codeDiscord = $_SESSION['code'];
		$data_token = json_encode([
			'code' => $codeIntra,
			'client_id' => $_ENV['API_UID'],
			'client_secret' => $_ENV['API_SECRET'],
			'grant_type' => 'authorization_code',
			'redirect_uri' => $_ENV['DOMAIN'].'/connected'
		]);
		if (is_string($data_token)) {
			try {
				$response = Hyper::post('https://api.intra.42.fr/oauth/token', $data_token, ['Content-type' => 'application/json']);
			} catch (\Throwable $th) {
				return View::generatePage(400, 'code 003');
			}
			$tmp = $response->toArray();
			$token = $tmp['token_type'] . ' ' . $tmp['access_token'];
			try {
				$response = Hyper::get('https://api.intra.42.fr/v2/me', [], null, ['Authorization' => $token]);
			} catch (\Throwable $th) {
				return View::generatePage(400, 'code 004');
			}
			$tmp = $response->toArray();
			if (isset($tmp, $tmp['login'])) {
				$manager = new Manager();
				$waiting_for_connect = $manager->exec('SELECT discord_id, code FROM temp_auth WHERE code = :code',
					[':code' => [$codeDiscord, PDO::PARAM_STR]]);
				if ($waiting_for_connect !== false && count($waiting_for_connect) === 1) {
					$add_to_new = $manager->exec('INSERT INTO new_users (discord_id, intra_id) VALUES (:discord_id, :intra_id)',
						[':discord_id' => [$waiting_for_connect[0]['discord_id'], PDO::PARAM_INT], ':intra_id' => [$tmp['login'], PDO::PARAM_STR]]);
					if ($add_to_new !== false) {
						$del = $manager->exec('DELETE FROM temp_auth WHERE discord_id = :discord_id',
							[':discord_id' => [$waiting_for_connect[0]['discord_id'], PDO::PARAM_INT]]);
					} else {
						return View::generatePage(500, 'code 005');
					}
				} else {
					return View::generatePage(401, 'code 006');
				}
			}
			else
				return View::generatePage(403, 'code 007');
			return View::generatePage(201, 'connected');
		} else {
			return View::generatePage(500, 'code 008');
		}
	}
}