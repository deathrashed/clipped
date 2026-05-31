import { staticFile } from "remotion";
import type { ClippedRenderProps } from "../types";

export type HeroAsset = "cover" | "artistImage" | "logo" | "background";

export type ResolvedAssets = {
  coverSrc: string | null;
  logoSrc: string | null;
  artistImageSrc: string | null;
  backgroundSrc: string | null;
  hasCover: boolean;
  hasLogo: boolean;
  hasArtistImage: boolean;
  hasBackground: boolean;
};

export const resolveAssets = (props: ClippedRenderProps): ResolvedAssets => {
  const coverSrc = props.assets.coverSrc ? staticFile(props.assets.coverSrc) : null;
  const logoSrc = props.assets.logoSrc ? staticFile(props.assets.logoSrc) : null;
  const artistImageSrc = props.assets.artistImageSrc ? staticFile(props.assets.artistImageSrc) : null;
  const backgroundSrc = props.assets.backgroundSrc ? staticFile(props.assets.backgroundSrc) : null;

  return {
    coverSrc,
    logoSrc,
    artistImageSrc,
    backgroundSrc,
    hasCover: !!coverSrc,
    hasLogo: !!logoSrc,
    hasArtistImage: !!artistImageSrc,
    hasBackground: !!backgroundSrc,
  };
};

export const pickHero = (assets: ResolvedAssets, preferred: HeroAsset): string | null => {
  const map: Record<HeroAsset, (string | null)[]> = {
    cover: [assets.coverSrc, assets.artistImageSrc, assets.logoSrc],
    artistImage: [assets.artistImageSrc, assets.coverSrc],
    logo: [assets.logoSrc, assets.coverSrc],
    background: [assets.backgroundSrc, assets.coverSrc],
  };
  return map[preferred].find(Boolean) ?? null;
};
