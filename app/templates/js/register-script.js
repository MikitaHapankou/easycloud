document.getElementById("loginForm").addEventListener("submit", async (e) => {
            e.preventDefault();
            const login = document.getElementById("login").value;
            const password = document.getElementById("password").value;

            const res = await fetch("/users/add",{
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({login, password})
            })

            const data = await res.json();

            if (res.ok) {
                alert("Registration success");
                window.location.href = "/dashboard";
            } else {
                alert(data.detail);
            }
        });