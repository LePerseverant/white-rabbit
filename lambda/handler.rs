use std::error::Error;

use lambda_runtime::{error::HandlerError, lambda, Context};
use serde_json::Value;

fn lambda_handler(event: Value, context: Context) -> Result<String, HandlerError> {
    println!("{}", event);
    Ok("Hello from Lambda!".to_string())
}

fn main() -> Result<(), Box<dyn Error>> {
    lambda!(lambda_handler);
    Ok(())
}
