import Foundation

class AuthService {
    static let shared = AuthService()
    private init() {}

    // CAMBIA ESTA URL POR LA TUYA DE RENDER
    let baseURL = "https://sensores-api-2.onrender.com"

    func login(email: String, password: String) async throws -> LoginResponse {

        guard let url = URL(string: "\(baseURL)/login") else {
            throw URLError(.badURL)
        }

        // El backend pide: email, password
        let body: [String: Any] = [
            "email": email,
            "password": password
        ]

        let dataBody = try JSONSerialization.data(withJSONObject: body)

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = dataBody

        let (data, response) = try await URLSession.shared.data(for: request)

        if let http = response as? HTTPURLResponse {
            print("Status code:", http.statusCode)
        }

        let decoded = try JSONDecoder().decode(LoginResponse.self, from: data)
        return decoded
    }
}
