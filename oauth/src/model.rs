use serde::{Deserialize, Serialize};

#[derive(Deserialize, Serialize)]
pub struct CodeParam {
    pub code: String,
}

#[derive(Deserialize, Serialize, Debug)]
pub struct DataToken {
    pub code: String,
    pub client_id: String,
    pub client_secret: String,
    pub grant_type: String,
    pub redirect_uri: String,
}

#[derive(Deserialize, Serialize, Debug)]
pub struct ResToken {
    pub access_token: String,
    pub token_type: String,
}

#[derive(Deserialize, Serialize, Debug)]
pub struct User {
    pub id: u64,
    pub login: String,
    pub email: String,
}

#[derive(Debug)]
pub struct Person {
    pub omega_id:u64,
	pub discord_id:u64,
	pub intra_id:String,
}

#[derive(Debug)]
pub struct TempAuth {
	pub discord_id:u64,
	pub code:String,
}
