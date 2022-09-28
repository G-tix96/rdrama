import { useEffect, useState } from "react";

export function useRootContext() {
  const [
    {
      admin,
      id,
      username,
      censored,
      themeColor,
      siteName,
      nameColor,
      avatar,
      hat,
    },
    setContext,
  ] = useState({
    id: "",
    username: "",
    admin: false,
    censored: true,
    themeColor: "#ff66ac",
    siteName: "",
    nameColor: "",
    avatar: "",
    hat: "",
  });

  useEffect(() => {
    const root = document.getElementById("root");

    setContext({
      id: root.dataset.id,
      username: root.dataset.username,
      admin: root.dataset.admin === "True",
      censored: root.dataset.censored === "True",
      themeColor: root.dataset.themecolor,
      siteName: root.dataset.sitename,
      nameColor: root.dataset.namecolor,
      avatar: root.dataset.avatar,
      hat: root.dataset.hat,
    });
  }, []);

  return {
    id,
    admin,
    username,
    censored,
    themeColor,
    siteName,
    nameColor,
    avatar,
    hat,
  };
}
