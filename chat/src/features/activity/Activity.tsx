import React from "react";
import "./Activity.css";

const ACTIVITIES = [
  {
    icon: "circle",
    title: "Roulette",
    description: "Round and round the wheel of fate turns.",
  },
  {
    icon: "cards",
    title: "Blackjack",
    description: "Twenty one ways to change your life.",
  },
  {
    icon: "dollar-sign",
    title: "Slots",
    description: "Today's your lucky day.",
  },
  {
    icon: "dollar-sign",
    title: "Racing",
    description: "Make it all back at the track.",
  },
  { icon: "dollar-sign", title: "Crossing", description: "Take a load off." },
];

export function Activity() {
  return (
    <div className="Activity">
      {ACTIVITIES.map((activity) => (
        <section key={activity.title}>
          <i className={`fas fa-${activity.icon}`}></i>
            <h4>{activity.title}</h4>
        </section>
      ))}
    </div>
  );
}
