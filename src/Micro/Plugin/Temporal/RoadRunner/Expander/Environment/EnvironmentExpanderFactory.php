<?php

namespace Micro\Plugin\Temporal\RoadRunner\Expander\Environment;

use Micro\Plugin\Temporal\Configuration\TemporalPluginConfigurationInterface;

class EnvironmentExpanderFactory implements EnvironmentExpanderFactoryInterface
{
    public function __construct(private readonly TemporalPluginConfigurationInterface $pluginConfiguration)
    {

    }

    /**
     * {@inheritDoc}
     */
    public function create(): EnvironmentExpanderInterface
    {
        return new EnvironmentExpander($this->pluginConfiguration->getRoadRunnerConfig());
    }
}