<?php

namespace Micro\Plugin\Temporal\Workflow\DataConverter;

use Temporal\DataConverter\DataConverterInterface;

interface DataConverterFactoryInterface
{
    /**
     * @return DataConverterInterface
     */
    public function create(): DataConverterInterface;
}