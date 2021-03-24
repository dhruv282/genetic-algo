# Mimic Image using Genetic Algorithm

This program uses a genetic algorithm to mimic a given image using triangles.

[Python 3](https://www.python.org/downloads/) along with the [Pillow (PIL)](https://pillow.readthedocs.io/en/stable/), [random](https://docs.python.org/3/library/random.html), and [copy](https://docs.python.org/3/library/copy.html) packages are required to run this program.

## Running the program:
This solver requires exactly 6 arguments:

- `imagePath`: path of input image
- `numTriangles`: number of triangles to be used in the generated image
- `populationSize`: number of generated pictures in the sample space
- `crossoverRate`: rate of crossover in population (between 0 and 1)
- `mutationRate`: rate of mutating each triangle in a given image (between 0 and 1)
- `generations`: number of times to run selections


```shell
$ python3 mimicImage.py imagePath numTriangles populationSize crossoverRate mutationRate generations
```
### Example:
```shell
$ python3 mimicImage.py ./images/someImage.png 100 55 0.2 0.1 1000
```