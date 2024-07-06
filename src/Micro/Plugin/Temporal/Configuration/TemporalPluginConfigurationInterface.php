<?php

namespace Micro\Plugin\Temporal\Configuration;

use Micro\Plugin\Temporal\Configuration\Client\WorkflowClientConfigurationInterface;
use Micro\Plugin\Temporal\Configuration\RoadRunner\RoadRunnerConfigurationInterface;
use Micro\Plugin\Temporal\Configuration\Worker\WorkflowWorkerConfigurationInterface;

interface TemporalPluginConfigurationInterface
{
    public const CLIENT_DEFAULT = 'default';

    /**
     * @return array
     */
    public function getWorkflowClientNamesList(): array;

    /**
     * @param string $clientName
     *
     * @return WorkflowClientConfigurationInterface
     */
    public function getClientConfig(string $clientName): WorkflowClientConfigurationInterface;

    /**
     * @param string $workerName
     *
     * @return WorkflowWorkerConfigurationInterface
     */
    public function getWorkerConfig(string $workerName): WorkflowWorkerConfigurationInterface;

    /**
     * @return RoadRunnerConfigurationInterface
     */
    public function getRoadRunnerConfig(): RoadRunnerConfigurationInterface;
}