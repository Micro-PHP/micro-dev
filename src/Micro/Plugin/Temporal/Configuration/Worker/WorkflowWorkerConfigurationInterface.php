<?php

namespace Micro\Plugin\Temporal\Configuration\Worker;

use JetBrains\PhpStorm\ExpectedValues;
use Spiral\RoadRunner\Environment\Mode;
use Spiral\RoadRunner\EnvironmentInterface;

interface WorkflowWorkerConfigurationInterface extends EnvironmentInterface
{
    /**
     * @return string
     */
    public function getQueueName(): string;

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