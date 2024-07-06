<?php

namespace Micro\Plugin\Temporal\Configuration\RoadRunner;

use JetBrains\PhpStorm\ExpectedValues;
use Spiral\RoadRunner\Environment\Mode;

interface RoadRunnerConfigurationInterface
{
    /**
     * @return string
     */
    #[ExpectedValues(valuesFromClass: Mode::class)]
    public function getMode(): string;

    /**
     * @return string
     */
    public function getRelayAddress(): string;

    /**
     * @return string
     */
    public function getRPCAddress(): string;
}