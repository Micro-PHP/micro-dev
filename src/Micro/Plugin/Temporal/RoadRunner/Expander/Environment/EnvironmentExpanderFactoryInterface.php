<?php

namespace Micro\Plugin\Temporal\RoadRunner\Expander\Environment;

interface EnvironmentExpanderFactoryInterface
{
    /**
     * @return EnvironmentExpanderInterface
     */
    public function create(): EnvironmentExpanderInterface;
}