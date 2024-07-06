<?php

namespace Micro\Plugin\Temporal\RoadRunner\Expander\Environment;

use Micro\Plugin\Temporal\Configuration\RoadRunner\RoadRunnerConfigurationInterface;

class EnvironmentExpander implements EnvironmentExpanderInterface
{
    /**
     * @param RoadRunnerConfigurationInterface $roadRunnerConfiguration
     */
    public function __construct(private readonly RoadRunnerConfigurationInterface $roadRunnerConfiguration)
    {
    }

    /**
     * {@inheritDoc}
     */
    public function expand()
    {

        $_ENV['RR_MODE'] = $this->roadRunnerConfiguration->getMode();
        $_ENV['RR_RELAY'] = $this->roadRunnerConfiguration->getRelayAddress();
        $_ENV['RR_RPC'] = $this->roadRunnerConfiguration->getRPCAddress();
    }
}