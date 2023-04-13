<?php
namespace App\Model;

use App\View\View;
use PDO;
use PDOStatement;

class Manager {
	protected static ?PDO   $db = null;

	public function __construct()
	{
		if (is_null(self::$db))
		{
			try {
				$dsn = 'mysql:dbname=' . $_ENV['MYSQL_DATABASE'] . ';host=mariadb';
				self::$db = new PDO($dsn, $_ENV['MYSQL_USER'], $_ENV['MYSQL_PASSWORD']);
			} catch (\Throwable $th) {
				self::$db = null;
				View::generatePage(500, 'code 101');
				exit;
			}
		}   
	}

	public function exec(string $sql, ?array $fields = null) {
		$request = self::$db->prepare($sql);
		if ($request === false)
			return false;
		if ($fields !== null) {
			foreach ($fields as $key => [$val, $type]) {
				if ($request->bindValue($key, $val, $type) == false)
					return false;
			}
		}
		$listArray = false;
		if (!(
			$request->execute() 
			&& $request->setFetchMode(PDO::FETCH_ASSOC)
			&& ($listArray = $request->fetchAll()) !== false
			&& $request->closeCursor()
		))
			return false;
		return $listArray;
	}
}