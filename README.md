# Chess/Chest

A two-player chess game using the [pyxel](https://github.com/kitao/pyxel) library.

## Install

```
pip install .
```
Maybe check [pyxel's installation steps](https://github.com/kitao/pyxel?tab=readme-ov-file#how-to-install) if you have issues.

## Playing

Run
```
chess
```
or 
```
chess --anything-goes
```
to try an alternate set of "rules".


## Toroidal chess

Others have thought [about](https://en.wikipedia.org/wiki/Cylinder_chess#Related_variants) [toroidal](https://www.chessvariants.com/other.dir/torus.html) [chess](https://puzzling.stackexchange.com/questions/136828/ernie-and-the-toroidal-chess-board);
try out a version with 
```
chess --periodic
```
In this version, the pieces face off in the middle of the board like football players to avoid the kings initially being in check.

## Vibe-code disclaimer

Core chess rules were AI-generated, so open an issue if anything looks off.