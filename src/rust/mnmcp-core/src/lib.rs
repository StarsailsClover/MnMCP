//! MnMCP Core Library
//! 
//! Core functionality for MiniWorld to Minecraft protocol bridge

pub mod network;
pub mod protocol;
pub mod crypto;
pub mod bridge;

use tracing::{info, debug};

/// MnMCP Core version
pub const VERSION: &str = "0.1.0";

/// Initialize the core library
pub fn init() {
    tracing_subscriber::fmt::init();
    info!("MnMCP Core v{} initialized", VERSION);
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_version() {
        assert_eq!(VERSION, "0.1.0");
    }
}
