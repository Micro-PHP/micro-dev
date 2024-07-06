<?php

namespace Micro\Plugin\Temporal\Workflow\Client\Factory;

use Micro\Plugin\Temporal\Configuration\Client\WorkflowClientConfigurationInterface;
use Micro\Plugin\Temporal\Workflow\DataConverter\DataConverterFactoryInterface;
use Temporal\Client\GRPC\ServiceClient;
use Temporal\Client\WorkflowClient;
use Temporal\Client\WorkflowClientInterface;

class ClientFactory implements ClientFactoryInterface
{
    public function __construct(
        private readonly DataConverterFactoryInterface $dataConverterFactory
    )
    {
    }

    /**
     * {@inheritDoc}
     */
    public function create(WorkflowClientConfigurationInterface $clientConfiguration): WorkflowClientInterface
    {
        $host = sprintf('%s:%d',
            $clientConfiguration->getTemporalHost(),
            $clientConfiguration->getTemporalPort()
        );

       return WorkflowClient::create(
           ServiceClient::create($host),
           null,
           $this->dataConverterFactory->create()
       );
    }
}