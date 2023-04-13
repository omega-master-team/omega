<?php

namespace App\View;

use Exception;

class View {
	private static array	$errors = [
		400 => 'La syntaxe de la requête est erronée',
		401 => 'Accès limité',
		403 => 'Accès non autorisé',
		404 => 'Page non trouvée',
		405 => 'Méthode de requête non autorisée',
		418 => 'I’m a teapot',
		500 => 'Erreur interne du serveur.',
		503 => 'Maintenance en cours'
	];

	private static  function generateError(int $errorCode, string $pageErrorPos) : string {
		if ($errorCode < 400 || $errorCode > 600)
			throw new Exception('Code d\' erreur incorrect');
		if ($errorCode < 500)
			$state = 'Erreur Client - ' . $errorCode;
		else
			$state = 'Erreur Server - ' . $errorCode;
		http_response_code($errorCode);
		if (array_key_exists($errorCode, self::$errors))
			$state .= ' - ' . self::$errors[$errorCode];
		ob_start();
		?>
		<div class="page">
			<p class="error"><?= $state . ' ' . $pageErrorPos ?></p>
		</div>
		<?php
		return ob_get_clean();
	}

	public static function generatePage(int $code = 200, string $page, $data = null) {
		if ($code >= 400) {
			$pageContent = self::generateError($code, $page);
			$pageName = $code;
		} else {
			ob_start();
			require_once 'layout' . DIRECTORY_SEPARATOR . $page . '.php';
			$pageContent = ob_get_clean();
		}
		return require_once 'layout' . DIRECTORY_SEPARATOR . 'main.php';
	}
}
