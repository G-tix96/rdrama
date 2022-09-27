import React from "react";
import "./Username.css";

interface UsernameProps {
  avatar: string;
  color: string;
  name: string;
  hat?: string;
}

export function Username({ avatar, color, name, hat = "" }: UsernameProps) {
  return (
    <div className="Username">
      <div className="profile-pic-20-wrapper">
        <img alt={name} src={avatar} className="pp20" />
        {hat && (
          <img
            className="avatar-hat profile-pic-20-hat hat"
            loading="lazy"
            src={hat}
          />
        )}
      </div>
      <a
        className="userlink"
        style={{ color: `#${color}` }}
        target="_blank"
        href={`/@${name}`}
        rel="noopener noreferrer"
      >
        {name}
      </a>
    </div>
  );
}
