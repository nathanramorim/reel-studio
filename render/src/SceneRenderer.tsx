import React from "react";
import { Scene, Theme, Style } from "./types";
import { Title } from "./scenes/Title";
import { Highlight } from "./scenes/Highlight";
import { Quote } from "./scenes/Quote";
import { Flow } from "./scenes/Flow";
import { ListScene } from "./scenes/ListScene";
import { Compare } from "./scenes/Compare";
import { Chart } from "./scenes/Chart";
import { Cta } from "./scenes/Cta";

/** Único ponto que liga type -> componente (DUP-01): novo tipo de cena entra só aqui. */
export const SceneRenderer: React.FC<{ scene: Scene; theme: Theme; style: Style }> = ({
  scene, theme, style,
}) => {
  switch (scene.type) {
    case "title":
      return <Title text={scene.text ?? ""} theme={theme} style={style} />;
    case "highlight":
      return <Highlight text={scene.text ?? ""} theme={theme} style={style} />;
    case "quote":
      return <Quote text={scene.text ?? ""} theme={theme} style={style} />;
    case "flow":
      return <Flow steps={scene.steps ?? []} theme={theme} style={style} />;
    case "list":
      return <ListScene items={scene.items ?? []} theme={theme} style={style} />;
    case "compare":
      return <Compare left={scene.left} right={scene.right} theme={theme} style={style} />;
    case "chart":
      return <Chart values={scene.values ?? []} theme={theme} style={style} />;
    case "cta":
      return <Cta text={scene.text} theme={theme} style={style} />;
    default:
      return null;
  }
};
