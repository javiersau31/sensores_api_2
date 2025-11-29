@IBAction func btnIniciar(_ sender: UIButton) {
    Task {
        await doLogin()
    }
}

func doLogin() async {
    let email = lblUsuario.text ?? ""
    let password = lblPassword.text ?? ""

    do {
        let response = try await AuthService.shared.login(email: email, password: password)

        print("Token recibido:", response.token)
        print("Usuario:", response.usuario.nombre)

        UserDefaults.standard.set(response.token, forKey: "token")

        DispatchQueue.main.async {
            self.performSegue(withIdentifier: "goToHome", sender: self)
        }

    } catch {
        print("Error:", error)
        showAlert("Credenciales incorrectas o servidor caído.")
    }
}
