# `AddColorNoise`

_Added in v0.35.0_

Mix in noise with color, additionally weighted by an [A-weighting](https://en.wikipedia.org/wiki/A-weighting) curve. When `f_decay=0` this is equivalent to `AddGaussianNoise`, with an option for weighting it with an `A-weighting` curve. Otherwise, see: [Colors of Noise](https://en.wikipedia.org/wiki/Colors_of_noise).


## AddColorNoise API


[`min_snr_db`](#min_snr_db){ #min_snr_db }: `float` • unit: Decibel
:   :octicons-milestone-24: Default: `5.0`. Minimum signal-to-noise ratio in dB. A lower
    number means more noise.

[`max_snr_db`](#max_snr_db){ #max_snr_db }: `float` • unit: decibel
:   :octicons-milestone-24: Default: `40.0`. Maximum signal-to-noise ratio in dB. A
    greater number means less noise.

[`min_f_decay`](#min_f_decay){ #min_f_decay }: `float` • unit: 
:   :octicons-milestone-24: Default: `-6.0`. Minimum noise decay in db per octave.

[`max_f_decay`](#max_f_decay){ #max_f_decay }: `float` • unit: 
:   :octicons-milestone-24: Default: `6.0`. Maximum noise decay in db per octave.

Those values can be chosen from the following table:

| Colour   | `f_decay`  (db/octave)|
|----------|-----------------------|
| pink     |                 -3.01 |
| brown    |                 -6.02 |
| Brownian |                 -6.02 |
| red      |                 -6.02 |
| blue     |                  3.01 |
| azure    |                  3.01 |
| violet   |                  6.02 |
| white    |                   0.0 |

See [Colors of noise](https://en.wikipedia.org/wiki/Colors_of_noise) on Wikipedia about those values.

[`p`](#p){ #p }: `float` • range: [0.0, 1.0]
:   :octicons-milestone-24: Default: `0.5`. The probability of applying this transform.



[`p_apply_a_weighting`](#p_apply_a_weighting){ #p_apply_a_weighting }: `float` • range: [0.0, 1.0]
:   :octicons-milestone-24: Default: `0.0`. The probability of additionally weighting the transform using an `A-weighting` curve.

[`n_fft`](#n_fft){ #n_fft }: `int` • 
:   :octicons-milestone-24: Default: `128`. The number of points the decay curve is computed (for coloring white noise).
