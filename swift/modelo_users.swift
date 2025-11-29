import Foundation

struct UserData: Codable {
    let id: String
    let nombre: String
    let email: String
    let rol: String
}

struct LoginResponse: Codable {
    let mensaje: String
    let token: String
    let usuario: UserData
}