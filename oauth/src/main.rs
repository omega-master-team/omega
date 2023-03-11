use std::{env, io};

use actix_session::{storage::CookieSessionStore, Session, SessionMiddleware};
use actix_web::{get, web::{self}, App, HttpServer, HttpResponse, Result, http::{StatusCode, header::{ContentType}}, middleware, cookie::Key};
use model::DataToken;
use openssl::ssl::{SslAcceptor, SslMethod, SslFiletype};
use rusqlite::params;
use tokio_rusqlite::Connection;
use urlencoding::encode;

use crate::model::{ResToken, User, TempAuth};
mod model;

const		API_UID_KEY: &str = "API_UID";
const		API_SECRET_KEY: &str = "API_SECRET";
const		API_REDIRECT_KEY: &str = "API_REDIRECT";
const		DB_FILE_KEY: &str = "DB_FILE";
static mut	API_UID: String = String::new();
static mut	API_SECRET: String = String::new();
static mut	API_REDIRECT: String = String::new();
static mut	DB_FILE: String = String::new();

fn build_url() -> String {
	let mut url = "https://api.intra.42.fr/oauth/authorize?client_id=API_UID&redirect_uri=API_REDIRECT&response_type=code".to_string();
	unsafe {
		url = url.replace("API_UID", API_UID.as_str());
		let tmp: String = encode(API_REDIRECT.as_str()).to_string();
		url = url.replace("API_REDIRECT", tmp.as_str());
	}
	url
}

/// simple index handler
#[get("/api")]
async fn welcome(session: Session, query: web::Query<model::CodeParam>) -> Result<HttpResponse> {
	session.insert("discord_code", &query.code)?;
	// response
	let mut rep: String = include_str!("../static/home.html").to_string();
	rep = rep.replace("LINK_INTRA", build_url().as_str());
	Ok(HttpResponse::build(StatusCode::OK)
		.content_type(ContentType::html())
		.body(rep))
}

#[get("/")]
async fn readme() -> Result<HttpResponse> {
	Ok(HttpResponse::build(StatusCode::OK)
		.content_type(ContentType::html())
		.body(include_str!("../static/readme.html")))
}

async fn get_token(intra_code: &str) -> Result<String> {
	let data: DataToken;
	unsafe {
		data = DataToken { 
			code: (intra_code.to_string()),
			client_id: (API_UID.as_str().to_string()),
			client_secret: (API_SECRET.as_str().to_string()),
			grant_type: ("authorization_code".to_string()),
			redirect_uri: (API_REDIRECT.as_str().to_string())
		};
	}
	//println!("{:?}", data);
	let res = reqwest::Client::new()
		.post("https://api.intra.42.fr/oauth/token")
		.json(&data)
		.send()
		.await.unwrap();
	//println!("{:?}", res);
	let val: ResToken = serde_json::from_str(res.text().await.unwrap().as_str()).unwrap();
	let mut auth = "type token".to_string();
	auth = auth.replace("type", &val.token_type.as_str());
	auth = auth.replace("token", &val.access_token.as_str());
	//println!("{}", auth);
	Ok(auth)
}

async fn get_user(intra_token: String) -> Result<User> {
	let res = reqwest::Client::new()
		.get("https://api.intra.42.fr/v2/me")
		.header("Authorization", intra_token)
		.send()
		.await.unwrap().text().await.unwrap();
	let val: User = serde_json::from_str(res.as_str()).unwrap();
	//println!("{:?}", val);
	Ok(val)
}

#[get("/connected")]
async fn connected(session: Session, query: web::Query<model::CodeParam>) -> Result<HttpResponse> {
	let mut rep = include_str!("../static/connected.html").to_string();
	if let Some(discord) = session.get::<String>("discord_code")? {
		session.purge();
		//println!("dicord code: {:?}", discord);
		//println!("intra code: {:?}", query.code);
		let intra_token = get_token(query.code.as_str()).await.unwrap();
		let user: User = get_user(intra_token).await.unwrap();
		//println!("{:?}", user);
		// save db
		let mut db_file: String = String::new();
		unsafe {
			db_file = DB_FILE.as_str().to_string();
		}
		let conn = Connection::open(db_file).await.unwrap();
		// SELECT discord_id, code FROM temp_auth
		let mut people = conn
		.call(move |conn| {
			let mut stmt = conn.prepare("SELECT discord_id, code FROM temp_auth WHERE code = :code")?;
			let people = stmt
			.query_map(&[(":code", discord.as_str())], |row| {
				Ok(TempAuth {
					discord_id: row.get(0)?,
					code: row.get(1)?,
				})
			})?
			.collect::<Result<Vec<TempAuth>, rusqlite::Error>>()?;
			Ok::<_, rusqlite::Error>(people)
		}).await.unwrap();
		if people.len() == 1 { // a6ef76d2-32f1-4b49-8afd-53279699e541
			let person = people.pop().unwrap();
			//println!("{:?}", person);
			conn.call(move |conn| {
				// INSERT INTO new_users (discord_id, intra_id) VALUES (discord_id, user.login)
				conn.execute(
					"INSERT INTO new_users (discord_id, intra_id) VALUES (?1, ?2)",
					params![person.discord_id, user.login],
				).unwrap();
				// DELETE FROM temp_auth WHERE code=code
				conn.execute(
					"DELETE FROM temp_auth WHERE discord_id = ?1",
					params![person.discord_id],
				).unwrap();
			}).await;
			rep = rep.replace("CONNECT_STATUS", "Success, your discord and your intra are connected");
		} else {
			rep = rep.replace("CONNECT_STATUS", "<h1 class=\"error\">BAD REQUEST</h1>");
		}
	} else {
		session.purge();
		rep = rep.replace("CONNECT_STATUS", "<h1 class=\"error\">BAD REQUEST</h1>");
		return Ok(HttpResponse::build(StatusCode::BAD_REQUEST)
			.content_type(ContentType::html())
			.body(rep)
		)
	}

	// response
	Ok(HttpResponse::build(StatusCode::OK)
		.content_type(ContentType::html())
		.body(rep)
	)
}

macro_rules! svg_response {
    ($svg:expr) => {
        HttpResponse::build(StatusCode::OK)
            .content_type("image/svg+xml")
            .body($svg)
    }
}
/*
#[get("/logo_white.svg")]
async fn logo_white() -> Result<HttpResponse> {
	Ok(svg_response!(include_str!("../static/logo_white.svg")))
}


#[get("/logo_black.svg")]
async fn logo_black() -> Result<HttpResponse> {
	Ok(svg_response!(include_str!("../static/logo_black.svg")))
}
*/

#[get("/omega.svg")]
async fn omega() -> Result<HttpResponse> {
	Ok(svg_response!(include_str!("../static/omega.svg")))
}

#[get("/favicon.ico")]
async fn favicon() -> Result<HttpResponse> {
	Ok(svg_response!(include_str!("../static/omega.svg")))
}


#[actix_web::main] // or #[tokio::main]
async fn main() -> io::Result<()> {
	unsafe {
		API_UID = env::var(API_UID_KEY).unwrap_or_else(|_| {
			panic!("API UID not found in env")
		});
		//println!("{} {}", API_UID_KEY, API_UID);
		API_SECRET = env::var(API_SECRET_KEY).unwrap_or_else(|_| {
			panic!("API SECRET not found in env")
		});
		//println!("{} {}", API_SECRET_KEY, API_SECRET);
		API_REDIRECT = env::var(API_REDIRECT_KEY).unwrap_or_else(|_| {
			panic!("API REDIRECT not found in env")
		});
		//println!("{} {}", API_REDIRECT_KEY, API_REDIRECT);
		DB_FILE = env::var(DB_FILE_KEY).unwrap_or_else(|_| {
			panic!("Database file not found in env")
		});
		//println!("{} {}", DB_FILE_KEY, DB_FILE);
	}
    println!("ENV OK");
	let key: Key = actix_web::cookie::Key::generate();
    println!("Server starting...");
	let mut builder = SslAcceptor::mozilla_intermediate(SslMethod::tls()).unwrap();
    builder
        .set_private_key_file("/etc/letsencrypt/live/protocole-omega.tech/privkey.pem", SslFiletype::PEM)
        .unwrap();
    builder.set_certificate_chain_file("/etc/letsencrypt/live/protocole-omega.tech/fullchain.pem").unwrap();

	HttpServer::new(move || {
		App::new()
			// enable automatic response compression - usually register this first
			.wrap(middleware::Compress::default())
			// cookie session middleware
			.wrap(
				SessionMiddleware::builder(CookieSessionStore::default(), key.clone())
					//.cookie_same_site(SameSite::None)
                    .cookie_secure(false)
                    //.cookie_http_only(false)
                    .build(),
			)
			// enable logger - always register Actix Web Logger middleware last
			.wrap(middleware::Logger::default())
			.service(welcome)
			.service(connected)
			.service(omega)
			//.service(logo_white)
			//.service(logo_black)
			.service(favicon)
			.service(readme)
	})
	.bind_openssl("0.0.0.0:443", builder)?
	.run()
	.await
}
