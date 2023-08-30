import random
import warnings
from typing import Union

import numpy as np
from numpy.typing import NDArray

from audiomentations.core.transforms_interface import BaseWaveformTransform
from audiomentations.core.utils import convert_decibels_to_amplitude_ratio


def get_fade_mask(
    start_level_db: float,
    end_level_db: float,
    fade_time_samples: int,
):
    """
    :param start_level_db:
    :param end_level_db:
    :param fade_time_samples: How long does the fade last?
    :return:
    """
    fade_mask = np.linspace(
        start_level_db,
        end_level_db,
        num=fade_time_samples,
        dtype=np.float32,
    )
    fade_mask = convert_decibels_to_amplitude_ratio(fade_mask)
    return fade_mask


class GainTransition(BaseWaveformTransform):
    """
    Gradually change the volume up or down over a random time span. Also known as
    fade in and fade out. The fade works on a logarithmic scale, which is natural to
    human hearing.

    The way this works is that it picks two gains: a first gain and a second gain.
    Then it picks a time range for the transition between those two gains.
    Note that this transition can start before the audio starts and/or end after the
    audio ends, so the output audio can start or end in the middle of a transition.
    The gain starts at the first gain and is held constant until the transition start.
    Then it transitions to the second gain. Then that gain is held constant until the
    end of the sound.
    """

    supports_multichannel = True

    def __init__(
        self,
        min_gain_in_db: float = None,
        max_gain_in_db: float = None,
        min_gain_db: float = None,
        max_gain_db: float = None,
        min_duration: Union[float, int] = 0.2,
        max_duration: Union[float, int] = 6.0,
        duration_unit: str = "seconds",
        p: float = 0.5,
    ):
        """

        :param min_gain_in_db: Deprecated. Use min_gain_db instead
        :param max_gain_in_db: Deprecated. Use max_gain_db instead
        :param min_gain_db: Minimum gain
        :param max_gain_db: Maximum gain
        :param min_duration: Minimum length of transition. See also duration_unit.
        :param max_duration: Maximum length of transition. See also duration_unit.
        :param duration_unit: Defines the unit of the value of min_duration and max_duration.
            "fraction": Fraction of the total sound length
            "samples": Number of audio samples
            "seconds": Number of seconds
        :param p: The probability of applying this transform
        """
        super().__init__(p)

        if min_gain_db is not None and min_gain_in_db is not None:
            raise ValueError(
                "Passing both min_gain_db and min_gain_in_db is not supported. Use only"
                " min_gain_db."
            )
        elif min_gain_db is not None:
            self.min_gain_db = min_gain_db
        elif min_gain_in_db is not None:
            warnings.warn(
                "The min_gain_in_db parameter is deprecated. Use min_gain_db instead.",
                DeprecationWarning,
            )
            self.min_gain_db = min_gain_in_db
        else:
            self.min_gain_db = -24.0  # the default

        if max_gain_db is not None and max_gain_in_db is not None:
            raise ValueError(
                "Passing both max_gain_db and max_gain_in_db is not supported. Use only"
                " max_gain_db."
            )
        elif max_gain_db is not None:
            self.max_gain_db = max_gain_db
        elif max_gain_in_db is not None:
            warnings.warn(
                "The max_gain_in_db parameter is deprecated. Use max_gain_db instead.",
                DeprecationWarning,
            )
            self.max_gain_db = max_gain_in_db
        else:
            self.max_gain_db = 6.0  # the default

        assert self.min_gain_db <= self.max_gain_db

        assert min_duration > 0
        assert min_duration <= max_duration
        self.min_duration = min_duration
        self.max_duration = max_duration
        self.duration_unit = duration_unit

    def randomize_parameters(self, samples: NDArray[np.float32], sample_rate: int):
        super().randomize_parameters(samples, sample_rate)
        if self.parameters["should_apply"]:
            if self.duration_unit == "samples":
                min_duration_in_samples = self.min_duration
                max_duration_in_samples = self.max_duration
            elif self.duration_unit == "fraction":
                min_duration_in_samples = int(
                    round(self.min_duration * samples.shape[-1])
                )
                max_duration_in_samples = int(
                    round(self.max_duration * samples.shape[-1])
                )
            elif self.duration_unit == "seconds":
                min_duration_in_samples = int(round(self.min_duration * sample_rate))
                max_duration_in_samples = int(round(self.max_duration * sample_rate))
            else:
                raise ValueError("Invalid duration_unit")

            self.parameters["fade_time_samples"] = max(
                3, random.randint(min_duration_in_samples, max_duration_in_samples)
            )
            self.parameters["t0"] = random.randint(
                -self.parameters["fade_time_samples"] + 2,
                samples.shape[-1] - 2,
            )
            self.parameters["start_gain_db"] = random.uniform(
                self.min_gain_db, self.max_gain_db
            )
            self.parameters["end_gain_db"] = random.uniform(
                self.min_gain_db, self.max_gain_db
            )

    def apply(self, samples: NDArray[np.float32], sample_rate: int):
        num_samples = samples.shape[-1]
        fade_mask = get_fade_mask(
            start_level_db=self.parameters["start_gain_db"],
            end_level_db=self.parameters["end_gain_db"],
            fade_time_samples=self.parameters["fade_time_samples"],
        )
        start_sample_index = self.parameters["t0"]
        end_sample_index = start_sample_index + self.parameters["fade_time_samples"]
        if start_sample_index < 0:
            # crop fade_mask: shave off a chunk in the beginning
            num_samples_to_shave_off = abs(start_sample_index)
            fade_mask = fade_mask[num_samples_to_shave_off:]
            start_sample_index = 0

        if end_sample_index > num_samples:
            # crop fade_mask: shave off a chunk in the end
            num_samples_to_shave_off = end_sample_index - num_samples
            fade_mask = fade_mask[: fade_mask.shape[-1] - num_samples_to_shave_off]
            end_sample_index = num_samples

        samples = np.copy(samples)

        samples[..., start_sample_index:end_sample_index] *= fade_mask
        if start_sample_index > 0:
            samples[..., :start_sample_index] *= convert_decibels_to_amplitude_ratio(
                self.parameters["start_gain_db"]
            )
        if end_sample_index < num_samples:
            samples[..., end_sample_index:] *= convert_decibels_to_amplitude_ratio(
                self.parameters["end_gain_db"]
            )
        return samples
