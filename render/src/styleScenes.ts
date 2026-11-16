import React from "react";
import { Scene, Theme, Style } from "./types";
import { ForgePhrase, ForgeFlow, ForgeList, ForgeCompare, ForgeCta } from "./forge/ForgeScenes";
import { IsoPhrase, IsoFlow, IsoList, IsoCompare } from "./iso/scenes";

export type SceneComponent = React.FC<{ scene: Scene; theme: Theme; style: Style }>;

/** Variantes de cena por `style.id`; estilo ou tipo sem entrada usa o componente padrão (DUP-01). */
export const styleScenes: Record<string, Partial<Record<Scene["type"], SceneComponent>>> = {
  "isometric-pastel": {
    title: IsoPhrase,
    highlight: IsoPhrase,
    cta: IsoPhrase,
    flow: IsoFlow,
    list: IsoList,
    compare: IsoCompare,
  },
  "forge-motion": {
    title: ForgePhrase,
    highlight: ForgePhrase,
    flow: ForgeFlow,
    list: ForgeList,
    compare: ForgeCompare,
    cta: ForgeCta,
  },
};
