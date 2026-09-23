// Expose repo assets and pipeline runs to Remotion's public/ folder via symlinks.
//   public/assets -> ../../assets        (music, sfx, fonts)
//   public/runs   -> ../../data/runs     (pipeline outputs, incl. 06_timeline.json)
import { existsSync, symlinkSync } from "node:fs";
import { resolve } from "node:path";

const pub = resolve("public");
for (const [name, target] of [["assets", "../../assets"], ["runs", "../../data/runs"]]) {
  const link = resolve(pub, name);
  if (!existsSync(link)) symlinkSync(target, link, "dir");
}
