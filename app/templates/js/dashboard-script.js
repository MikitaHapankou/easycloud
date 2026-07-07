document.getElementById("logout-btn").addEventListener("click", () => {
        fetch ("/users/logout");
        window.location.href="/";
    });

    addEventListener("DOMContentLoaded", async (event) => {
        const res = await fetch("/dashboard/my", {
            credentials: "include"
        })

        const data = await res.json()

        if (res.ok) {
            document.querySelector(".username").innerText = data.username;

            const itemMap = {};
            const rootItems = [];

            data.files.forEach(item => {
               itemMap[item.id] = { ...item, children: [] };
            });

            data.files.forEach(item => {
               const mappedItem = itemMap[item.id];

               if (item["parent_id"] === "filesContainer"){
                   rootItems.push(mappedItem);
               }
               else{
                   const parent = itemMap[item["parent_id"]];
                   if (parent) {
                       parent.children.push(mappedItem);
                   }
               }
            });

            const renderTree = (nodes) => {
                nodes.forEach(node => {
                    let parentElement = document.getElementById(node["parent_id"]);

                    if (parentElement && parentElement.classList.contains("dir")) {
                        parentElement = parentElement.querySelector(".dir-children");
                    }

                    if (node.type === 'dir'){
                        const dir = document.createElement("div");
                        dir.classList.add("dir");
                        dir.id = node["id"];

                        const dirHeader = document.createElement("div");
                        dirHeader.classList.add("dir-header");
                        dirHeader.innerText = node.name;

                        const childrenContainer = document.createElement("div");
                        childrenContainer.classList.add("dir-children");

                        dir.appendChild(dirHeader);
                        dir.appendChild(childrenContainer);

                        parentElement.appendChild(dir);

                        renderTree(node.children);
                    }
                    else {
                        const fileWrapper = document.createElement("div");
                        fileWrapper.classList.add("file-wrapper");

                        const a = document.createElement("a");
                        a.classList.add("file-item");
                        a.href = `/dashboard/download/${node["path"]}`;
                        a.innerText = node["name"];

                        const deleteBtn = document.createElement("button");
                        deleteBtn.innerText = "Delete";
                        deleteBtn.classList.add("delete-btn");

                        deleteBtn.onclick = async () => {
                            try{
                                const response = await fetch (`/dashboard/delete-file/${node.path}`,{
                                    method: "GET"
                                })

                                const result = await response.json();

                                if (response.ok) {
                                        alert("Success");
                                        window.location.reload();
                                    } else {
                                        alert("Error: " + result.detail);
                                    }
                            }
                            catch (error){
                                alert("An error occured");
                            }
                        };

                        fileWrapper.appendChild(a);
                        fileWrapper.appendChild(deleteBtn);

                        parentElement.appendChild(fileWrapper);
                    }
                })
            }

            renderTree(rootItems);

        } else {
            window.location.href = "/";
        }

        const inputElement = document.getElementById("input");
        inputElement.addEventListener("change", handleFiles);

        async function handleFiles() {
            const fileList = this.files;
            const file = fileList[0];
            if (file){
                try {
                    const formData = new FormData();
                    formData.append('uploaded_file', file);
                    const response = await fetch(`/dashboard/add-file`, {
                        method: "POST",
                        body: formData
                    });

                    const result = await response.json();

                    if (response.ok) {
                        alert("Success");
                        window.location.reload();
                    } else {
                        alert("Error: " + result.detail);
                    }

                }
                catch (error){
                    alert("An error occured");
                }

            }
        }
    });