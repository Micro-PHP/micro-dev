<?php

namespace Micro\Plugin\Temporal;

use Micro\Framework\BootConfiguration\Configuration\PluginConfiguration;
use Micro\Plugin\Temporal\Configuration\Client\WorkflowClientConfiguration;
use Micro\Plugin\Temporal\Configuration\Client\WorkflowClientConfigurationInterface;
use Micro\Plugin\Temporal\Configuration\RoadRunner\RoadRunnerConfiguration;
use Micro\Plugin\Temporal\Configuration\RoadRunner\RoadRunnerConfigurationInterface;
use Micro\Plugin\Temporal\Configuration\TemporalPluginConfigurationInterface;
use Micro\Plugin\Temporal\Configuration\Worker\WorkflowWorkerConfiguration;
use Micro\Plugin\Temporal\Configuration\Worker\WorkflowWorkerConfigurationInterface;

class TemporalPluginConfiguration extends PluginConfiguration implements TemporalPluginConfigurationInterface
{

    const CFG_CLIENT_LIST = 'TEMPORAL_CLIENT_LIST';

    /**
     * {@inheritDoc}
     */
    public function getWorkflowClientNamesList(): array
    {
        return $this->explodeStringToArray(
            $this->configuration->get(self::CFG_CLIENT_LIST, self::CLIENT_DEFAULT)
        );
    }

    /**
     * {@inheritDoc}
     */
    public function getClientConfig(string $clientName): WorkflowClientConfigurationInterface
    {
        return new WorkflowClientConfiguration(
            configuration: $this->configuration,
            configRoutingKey: $clientName
        );
    }

    /**
     * {@inheritDoc}
     */
    public function getWorkerConfig(string $workerName): WorkflowWorkerConfigurationInterface
    {
        return new WorkflowWorkerConfiguration(
            configuration: $this->configuration,
            configRoutingKey: $workerName
        );
    }

    /**
     * {@inheritDoc}
     */
    public function getRoadRunnerConfig(): RoadRunnerConfigurationInterface
    {
        return new RoadRunnerConfiguration($this->configuration, '');
    }
}