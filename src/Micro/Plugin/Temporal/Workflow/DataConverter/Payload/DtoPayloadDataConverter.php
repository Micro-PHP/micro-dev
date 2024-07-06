<?php

namespace Micro\Plugin\Temporal\Workflow\DataConverter\Payload;

use Micro\Library\DTO\Object\AbstractDto;
use Micro\Library\DTO\SerializerFacadeInterface;
use Temporal\Api\Common\V1\Payload;
use Temporal\DataConverter\Converter;
use Temporal\DataConverter\PayloadConverterInterface;
use Temporal\DataConverter\Type;

class DtoPayloadDataConverter extends Converter implements PayloadConverterInterface
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
    public function getEncodingType(): string
    {
        return 'MicroDtoObject';
    }

    /**
     * {@inheritDoc}
     */
    public function toPayload($value): ?Payload
    {
        if(!($value instanceof AbstractDto)) {
            return null;
        }

        return $this->create($this->serializerFacade->toJsonTransfer($value));
    }

    /**
     * {@inheritDoc}
     */
    public function fromPayload(Payload $payload, Type $type)
    {
        return $this->serializerFacade->fromJsonTransfer($payload->getData());
    }
}