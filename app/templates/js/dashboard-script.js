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
            document.querySelector("#username").innerText = data.username;

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
                        dir.classList.add("dir", "mb-1");
                        dir.id = node["id"];

                        const dirHeader = document.createElement("div");
                        dirHeader.classList.add("dir-header", "font-semibold", "text-gray-800", "py-2", "px-3");
                        dirHeader.innerText = node.name;

                        const childrenContainer = document.createElement("div");
                        childrenContainer.classList.add("dir-children", "pl-4", "flex", "flex-col", "gap-1");

                        dir.appendChild(dirHeader);
                        dir.appendChild(childrenContainer);

                        parentElement.appendChild(dir);

                        renderTree(node.children);
                    }
                    else {
                        const fileWrapper = document.createElement("div");
                        fileWrapper.classList.add("file-wrapper", "flex", "items-center", "justify-between", "gap-3", "py-2", "px-3", "rounded-lg", "hover:bg-gray-50", "transition-colors");

                        const a = document.createElement("a");
                        a.classList.add("file-item", "text-gray-700", "hover:text-blue-400", "truncate", "flex-1");
                        a.href = `/dashboard/download/${node["path"]}`;
                        a.innerText = node["name"];

                        const deleteBtn = document.createElement("button");
                        deleteBtn.innerText = "Delete";
                        deleteBtn.classList.add("delete-btn", "text-sm", "font-medium", "text-red-500", "border", "border-red-500", "rounded-md", "px-3", "py-1", "hover:bg-red-500", "hover:text-white", "transition-colors");
                        deleteBtn.type = "button";

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