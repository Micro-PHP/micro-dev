<?php

namespace Micro\Plugin\Temporal\Workflow\DataConverter;

use Micro\Library\DTO\SerializerFacadeInterface;
use Micro\Plugin\Temporal\Workflow\DataConverter\Payload\DtoPayloadDataConverter;
use Temporal\DataConverter\BinaryConverter;
use Temporal\DataConverter\DataConverter;
use Temporal\DataConverter\DataConverterInterface;
use Temporal\DataConverter\JsonConverter;
use Temporal\DataConverter\NullConverter;
use Temporal\DataConverter\ProtoJsonConverter;

class DataConverterFactory implements DataConverterFactoryInterface
{
    /**
     * @param SerializerFacadeInterface $serializerFacade
     */
    public function __construct(private readonly SerializerFacadeInterface $serializerFacade)
    {

    }

    /**
     * {@inheritDoc}
     */
    public function create(): DataConverterInterface
    {
        return new DataConverter(
            new DtoPayloadDataConverter($this->serializerFacade),
            new JsonConverter(),
            new NullConverter(),
            new BinaryConverter(),
            new ProtoJsonConverter(),
        );
    }
}