<?php

namespace Micro\Plugin\Temporal\Workflow\Client\Repository;

use Micro\Plugin\Temporal\Configuration\TemporalPluginConfigurationInterface;
use Micro\Plugin\Temporal\Workflow\Client\Factory\ClientFactoryInterface;

class ClientRepositoryFactory implements ClientRepositoryFactoryInterface
{
    /**
     * @param ClientFactoryInterface $clientFactory
     * @param TemporalPluginConfigurationInterface $pluginConfiguration
     */
    public function __construct(
        private readonly ClientFactoryInterface $clientFactory,
        private readonly TemporalPluginConfigurationInterface $pluginConfiguration
    )
    {
    }

    /**
     * {@inheritDoc}
     */
    public function create(): ClientRepositoryInterface
    {
        return new ClientRepository(
            $this->clientFactory,
            $this->pluginConfiguration
        );
    }
}