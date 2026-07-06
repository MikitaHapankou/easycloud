document.getElementById("loginForm").addEventListener("submit", async (e) => {
            e.preventDefault();
            const login = document.getElementById("login").value;
            const password = document.getElementById("password").value;

            const res = await fetch("/users/login",{
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({login, password})
            })

            if (res.ok) {
                alert("Login success");
                window.location.href = "/dashboard";
            } else {
                alert(data.detail);
            }
        });