<?php

namespace Micro\Plugin\Temporal\Workflow\Client\Repository;

use Micro\Plugin\Temporal\Configuration\TemporalPluginConfigurationInterface;
use Micro\Plugin\Temporal\Workflow\Client\Factory\ClientFactoryInterface;
use Temporal\Client\WorkflowClientInterface;

class ClientRepository implements ClientRepositoryInterface
{
    private array $clientCollection;

    /**
     * @param ClientFactoryInterface $clientFactory
     * @param TemporalPluginConfigurationInterface $pluginConfiguration
     */
    public function __construct(
        private readonly ClientFactoryInterface $clientFactory,
        private readonly TemporalPluginConfigurationInterface $pluginConfiguration
    )
    {
        $this->clientCollection = [];
    }

    /**
     * {@inheritDoc}
     */
    public function client(string $clientName): WorkflowClientInterface
    {
        if(!array_key_exists($clientName, $this->clientCollection)) {
            $this->clientCollection[$clientName] = $this->clientFactory->create(
                $this->pluginConfiguration->getClientConfig($clientName)
            );
        }

        return $this->clientCollection[$clientName];
    }
}